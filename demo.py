from os import path
from fractions import Fraction
import matplotlib.pyplot as plt
import numpy as np
import fmpy
import configuration
import master
import analytical
import evaluation


def current_dir():
    """The current directory"""
    return path.dirname(path.abspath(__file__))


def fmu_dir():
    """The path to the directory with FMUs"""
    return path.join(current_dir(), 'FMUs')


def system_parameters():
    """Monolithic model parameters"""
    return {'Monolithic': {
        'J_Omega2Tau': 10., 'J_Tau2Omega': 10., 'c_Omega2Tau': 1., 'c_Tau2Omega': 1., 'ck': 1.,
        'd_Omega2Tau': 1., 'd_Tau2Omega': 2., 'dk': 2.,
        'omega0_Omega2Tau': 0.1, 'omega0_Tau2Omega': 0.1, 'phi0_Omega2Tau': 0.1, 'phi0_Tau2Omega': 0.2
    }}


def partitioned_system_parameters():
    """Partitioned parameters"""
    parameters = system_parameters()
    return {
        "Tau2Omega": {
            "J": parameters["Monolithic"]["J_Tau2Omega"],
            "c": parameters["Monolithic"]["c_Tau2Omega"], "d": parameters["Monolithic"]["d_Tau2Omega"],
            "phiThis0": parameters["Monolithic"]["phi0_Tau2Omega"], "omegaThis0": parameters["Monolithic"]["omega0_Tau2Omega"]
        },
        "Omega2Tau": {
            "J": parameters["Monolithic"]["J_Omega2Tau"],
            "c": parameters["Monolithic"]["c_Omega2Tau"], "d": parameters["Monolithic"]["d_Omega2Tau"],
            "ck": parameters["Monolithic"]["ck"], "dk": parameters["Monolithic"]["dk"],
            "phiThis0": parameters["Monolithic"]["phi0_Omega2Tau"], "omegaThis0": parameters["Monolithic"]["omega0_Omega2Tau"],
            "phiOther0": parameters["Monolithic"]["phi0_Tau2Omega"]
        }
    }

def monolithic_solution(step_size, tEnd):
    """A monolithic solution of the configuration"""
    slaves, connections = configuration.read(fmu_dir(), 'monolithic.xml')
    fmus = {name: master.load_fmu(name, description['archivePath']) for name, description in slaves.items()}

    monolithic_result = master.run(fmus, connections, step_size, tEnd, parameters=system_parameters())
    results = {
        ('Omega2Tau', 'tauThis'): monolithic_result['Monolithic', 'tau'],
        ('Omega2Tau', 'omegaOther'): monolithic_result['Monolithic', 'omega'],
        ('Tau2Omega', 'omegaThis'): monolithic_result['Monolithic', 'omega'],
        ('Tau2Omega', 'tauOther'): monolithic_result['Monolithic', 'tau']
    }
    return results

def co_simulations():
    """Co-simulations used in this demo"""
    sequences = {
        'Jacobi': None,
        'Gauss-Seidel': ['Tau2Omega', 'Omega2Tau']
    }
    slaves, connections = configuration.read(fmu_dir(), 'example.xml')
    fmus = {name: master.load_fmu(name, description['archivePath']) for name, description in slaves.items()}
    return fmus, connections, sequences


def run_simulations(slaves, connections, sequences, step_size, tEnd):
    """
    Runs co-simulations and the analytical calculation for the give step size.
    """
    results = {
        name: master.run(slaves, connections, step_size, tEnd, sequence, partitioned_system_parameters())
        for name, sequence in sequences.items()
    }
    return results


def plot_signals():
    """Simple time plot of the signals in the graph"""
    slaves, connections, sequences = co_simulations()
    step_size = 0.5
    tEnd = 50.
    results = run_simulations(slaves, connections, sequences, step_size, tEnd)
    results['monolithic'] = monolithic_solution(step_size, tEnd)
    color = {'Gauss-Seidel': 'g', 'Jacobi': 'b', 'monolithic': 'r--'}

    _, (axVelocity, axTorque) = plt.subplots(2, 1, sharex=True)
    for name, result in results.items():
        ts = step_size * np.arange(len(result['Omega2Tau', 'tauThis']))
        axVelocity.plot(ts, result['Tau2Omega', 'omegaThis'], color[name], label=name)
        axVelocity.set_xlim(min(ts), max(ts))
        axTorque.plot(ts, result['Omega2Tau', 'tauThis'], color[name], label=name)
        axTorque.set_xlim(min(ts), max(ts))

    axVelocity.set_title('velocity')
    axTorque.set_title('torque')
    axTorque.legend()
    axVelocity.legend()
    plt.show()


def analysis_plot(dataX, dataY, sequences = 0, xScale = 'linear', yScale = 'linear', titles = [], legends = []):
    """ The script fpr ploting data for mthod residual_analysis()"""
    
    _, axs = plt.subplots(len(dataY), 1, sharex=True)   
    color = {'Gauss-Seidel': 'g', 'Jacobi': 'b', 'monolithic': 'r--'}
    if len(dataY) > 1:
        for ax, i in zip(axs, range(len(dataY))):    
            if sequences != 0:
                for sequence in sequences:    
                    ax.plot(dataX, dataY[i][sequence], color[sequence], label = ''.join([str(sequence) if legends == [] else legends[i]]))                     
            else:
                ax.plot(dataX, dataY[i], color[sequence], label = legends[i])
            ax.set_xlim(float(min(dataX)), float(max(dataX)))
            ax.set_xscale(xScale)
            ax.set_yscale(yScale)
            ax.legend()
            if titles != []:
                ax.set_title(titles[i])
    else:            
        if sequences != 0:
            for sequence in sequences:
                axs.plot(dataX, dataY[0][sequence], color[sequence], label = ''.join([str(sequence) if legends == [] else legends]))
        else:
            axs.plot(dataX, dataY[0], color[sequence], label = legends)
        axs.set_xscale(xScale)
        axs.set_yscale(yScale)
        axs.legend()
        if titles != []:
            axs.set_title(titles)
    plt.show()


def residual_analysis():
    """
    The analysis of total power residual and its comparison to the global error.
    """
    slaves, connections, sequences = co_simulations()
    step_sizes = list(map(Fraction, np.logspace(-1, 0, num=5)))
    tEnd = 50.
    tot_pow_residuals = {sequence: [] for sequence in sequences} 
    power_errors = {sequence: [] for sequence in sequences}
    conn_def_omega = {sequence: [] for sequence in sequences}
    conn_def_tau = {sequence: [] for sequence in sequences}

    for step_size in step_sizes:
        results = run_simulations(slaves, connections, sequences, step_size, tEnd)
        monolithic = monolithic_solution(step_size, tEnd)
        monolithic_power = np.array(monolithic['Omega2Tau','tauThis'])*monolithic['Tau2Omega','omegaThis']
            
        for sequence in sequences:
            tot_pow_residuals[sequence].append(
                evaluation.total_power_residual(
                    connections, results[sequence], step_size,
                    ('Omega2Tau', 'omegaOther'), ('Tau2Omega', 'tauOther')
                )
            )

            power = np.array(results[sequence]['Tau2Omega','tauOther'])*results[sequence]['Omega2Tau','omegaOther']

            power_errors[sequence].append(step_size*np.cumsum( np.abs(power - monolithic_power) )[-1])
            
            input_defect = evaluation.connection_defects(connections, results[sequence])
            conn_def_omega[sequence].append( step_size*np.cumsum( np.abs(input_defect['Tau2Omega', 'tauOther']))[-1] )
            conn_def_tau[sequence].append( step_size*np.cumsum( np.abs(input_defect['Omega2Tau', 'omegaOther']))[-1] )
    
    analysis_plot(step_sizes, [tot_pow_residuals, power_errors], sequences, 'log', 'log', ['Total power residual', 'Total error power' ])
    analysis_plot(step_sizes, [conn_def_omega, conn_def_tau], sequences, 'linear', 'linear', ['Omega defect','Torque defect'])
   


if __name__ == '__main__':
    plot_signals() 
    residual_analysis()
