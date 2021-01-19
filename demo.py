from os import path
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


def monolithic_solution(step_size, tEnd):
    """A monolithic solution of the configuration"""
    fmu = path.join(fmu_dir(), 'TwoMassRotationalOscillator.fmu')
    slaves, connections = configuration.read(fmu_dir(), 'monolithic.xml')
    fmus = {name: master.load_fmu(name, description['archivePath']) for name, description in slaves.items()}
    parameters = {name: description['parameters'] for name, description in slaves.items()}

    monolithic_result = master.run(fmus, connections, step_size, tEnd, parameters=parameters)
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
        'Gauss-Seidel 12': ['Omega2Tau', 'Tau2Omega'],
        'Gauss-Seidel 21': ['Tau2Omega', 'Omega2Tau']
    }
    slaves, connections = configuration.read(fmu_dir(), 'example.xml')
    fmus = {name: master.load_fmu(name, description['archivePath']) for name, description in slaves.items()}
    parameters = {name: description['parameters'] for name, description in slaves.items()}
    return fmus, connections, sequences, parameters


def run_simulations(slaves, connections, sequences, step_size, tEnd, parameters):
    """
    Runs co-simulations and the analytical calculation for the give step size.
    """
    results = {
        name: master.run(slaves, connections, step_size, tEnd, sequence, parameters)
        for name, sequence in sequences.items()
    }
    return results


def plot_signals():
    """Simple time plot of the signals in the graph"""
    slaves, connections, sequences, parameters = co_simulations()
    step_size = 1e-1
    tEnd = 100.
    results = run_simulations(slaves, connections, sequences, step_size, tEnd, parameters)
    results['monolithic'] = monolithic_solution(step_size, tEnd)

    _, (axVelocity, axTorque) = plt.subplots(2, 1, sharex=True)
    for name, result in results.items():
        ts = step_size * np.arange(len(result['Omega2Tau', 'tauThis']))
        axVelocity.plot(ts, result['Tau2Omega', 'omegaThis'], label=name)
        axTorque.plot(ts, result['Omega2Tau', 'tauThis'], label=name)

    axVelocity.set_title('velocity')
    axTorque.set_title('torque')
    axTorque.legend()
    plt.show()


def plot_residual_analysis(dataX, dataY, sequences = 0, xScale = 'linear', yScale = 'linear', titles = [], legends = []):
    """ The script fpr ploting data for mthod residual_analysis()"""
    
    _, axs = plt.subplots(len(dataY), 1, sharex=True)   
    if len(dataY) > 1:
        for ax, i in zip(axs, range(len(dataY))):    
            if sequences != 0:
                for sequence in sequences:    
                    ax.plot(dataX, dataY[i][sequence], label = ''.join([str(sequence) if legends == [] else legends[i]]))                     
            else:
                ax.plot(dataX, dataY[i], label = legends[i])
            ax.set_xscale(xScale)
            ax.set_yscale(yScale)
            ax.legend()
            if titles != []:
                ax.set_title(titles[i])
    else:            
        if sequences != 0:
            for sequence in sequences:
                axs.plot(dataX, dataY[0][sequence], label = ''.join([str(sequence) if legends == [] else legends]))
        else:
            axs.plot(dataX, dataY[0], label = legends)
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
    slaves, connections, sequences, parameters = co_simulations()
    step_sizes = [1 / den for den in 2 ** np.arange(1, 10)]
    tEnd = 50.
    torque_errors = {sequence: [] for sequence in sequences}
    velocity_errors = {sequence: [] for sequence in sequences}
    tot_pow_residuals = {sequence: [] for sequence in sequences} 
    power_errors = {sequence: [] for sequence in sequences}
    conn_def_omega = {sequence: [] for sequence in sequences}
    conn_def_tau = {sequence: [] for sequence in sequences}

    for step_size in step_sizes:
        results = run_simulations(slaves, connections, sequences, step_size, tEnd, parameters)
        monolithic = monolithic_solution(step_size, tEnd)
        Monolithic_power = np.array(monolithic['Omega2Tau','tauThis'])*monolithic['Tau2Omega','omegaThis']
            
        for sequence in sequences:
            tot_pow_residuals[sequence].append(
                evaluation.total_power_residual(
                    connections, results[sequence], step_size,
                    ('Omega2Tau', 'omegaOther'), ('Tau2Omega', 'tauOther')
                )
            )
            errs = evaluation.global_error(results[sequence], monolithic, step_size)
            torque_errors[sequence].append(errs['Omega2Tau', 'tauThis'])
            velocity_errors[sequence].append(errs['Tau2Omega', 'omegaThis'])

            power = np.array(results[sequence]['Omega2Tau','tauThis'])*results[sequence]['Tau2Omega','omegaThis']

            power_errors[sequence].append(step_size*np.cumsum( np.abs(power - Monolithic_power) )[-1])
            
            input_defect = evaluation.connection_defects(connections, results[sequence])
            conn_def_omega[sequence].append( step_size*np.cumsum( np.abs(input_defect['Tau2Omega', 'tauOther']))[-1] )
            conn_def_tau[sequence].append( step_size*np.cumsum( np.abs(input_defect['Omega2Tau', 'omegaOther']))[-1] )
    
    plot_residual_analysis(step_sizes, [tot_pow_residuals, torque_errors, velocity_errors, power_errors], sequences, 'log', 'log', ['Total power residual','Tau global error','Omega global error', 'Power error' ])
    plot_residual_analysis(step_sizes, [conn_def_omega, conn_def_tau], sequences, 'linear', 'linear', ['Omega defect','Tau defect'])
   


if __name__ == '__main__':
    #plot_signals() 
    residual_analysis()
