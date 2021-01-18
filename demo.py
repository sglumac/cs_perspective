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


def monolitic_solution(step_size, tEnd):
    """A monolithic solution of the configuration"""
    fmu = path.join(fmu_dir(), 'TwoMassRotationalOscillator.fmu')
    fmpy_result = fmpy.simulate_fmu(fmu, start_time=0, stop_time=tEnd, step_size=step_size)
    ts = fmpy_result['time']
    results = {
        ('OscillatorOmega2Tau', 'tauThis'): (ts, fmpy_result['tau_1']),
        ('OscillatorOmega2Tau', 'omegaOther'): (ts, fmpy_result['omega_2']),
        ('OscillatorTau2Omega', 'omegaThis'): (ts, fmpy_result['omega_2']),
        ('OscillatorTau2Omega', 'tauOther'): (ts, fmpy_result['tau_1'])
    }
    return results

def co_simulations():
    """Co-simulations used in this demo"""
    sequences = {
        'Jacobi': None,
        'Gauss-Seidel 12': ['Alpha', 'Engine', 'Inertia'],
        'Gauss-Seidel 21': ['Alpha', 'Inertia', 'Engine']
    }
    slaves, connections = configuration.read(fmu_dir(), 'example.xml')
    fmus = {name: master.load_fmu(name, description['archivePath']) for name, description in slaves.items()}
    return fmus, connections, sequences


def run_simulations(slaves, connections, sequences, step_size):
    """
    Runs co-simulations and the analytical calculation for the give step size.
    """
    tEnd = 10.
    results = {
        name: master.run(slaves, connections, step_size, tEnd, sequence, {'Engine': {'w_omega': 3}})
        for name, sequence in sequences.items()
    }
    return results, analytical.solution(step_size, tEnd)


def plot_signals():
    """Simple time plot of the signals in the graph"""
    slaves, connections, sequences = co_simulations()
    step_size = 1e-1
    results, analytic  = run_simulations(slaves, connections, sequences, step_size)
    results['analytical'] = analytic

    _, (axVelocity, axTorque) = plt.subplots(2, 1, sharex=True)
    for name, result in results.items():
        ts = step_size * np.arange(len(result['Inertia', 'velocity']))
        axVelocity.plot(ts, result['Inertia', 'velocity'], label=name)
        axTorque.plot(ts, result['Engine', 'torque'], label=name)

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
    slaves, connections, sequences = co_simulations()
    step_sizes = [1 / den for den in 2 ** np.arange(1, 10)]
    torque_errors = {sequence: [] for sequence in sequences}
    velocity_errors = {sequence: [] for sequence in sequences}
    tot_pow_residuals = {sequence: [] for sequence in sequences} 
    power_errors = {sequence: [] for sequence in sequences}
    conn_def_alpha = {sequence: [] for sequence in sequences}
    conn_def_velocity = {sequence: [] for sequence in sequences}
    conn_def_torque = {sequence: [] for sequence in sequences}

    for step_size in step_sizes:
        results, analytic = run_simulations(slaves, connections, sequences, step_size)
        Analytic_power = np.array(analytic['Engine','torque'])*analytic['Inertia','velocity']
            
        for sequence in sequences:
            tot_pow_residuals[sequence].append(
                evaluation.total_power_residual(
                    connections, results[sequence], step_size,
                    ('Inertia', 'torque'), ('Engine', 'velocity')
                )
            )
            errs = evaluation.global_error(results[sequence], analytic, step_size)
            torque_errors[sequence].append(errs['Engine', 'torque'])
            velocity_errors[sequence].append(errs['Inertia', 'velocity'])

            power = np.array(results[sequence]['Engine','torque'])*results[sequence]['Inertia','velocity']

            power_errors[sequence].append(step_size*np.cumsum( np.abs(power - Analytic_power) )[-1])
            
            input_defect = evaluation.connection_defects(connections, results[sequence])
            conn_def_alpha[sequence].append( step_size*np.cumsum( np.abs(input_defect['Engine', 'alpha']))[-1] )
            conn_def_velocity[sequence].append( step_size*np.cumsum( np.abs(input_defect['Engine', 'velocity']))[-1] )
            conn_def_torque[sequence].append( step_size*np.cumsum( np.abs(input_defect['Inertia', 'torque']))[-1] )
    
    plot_residual_analysis(step_sizes, [tot_pow_residuals, torque_errors, velocity_errors, power_errors], sequences, 'log', 'log', ['Total power residual','Torque global error','Velocity global error', 'Power error' ])
    plot_residual_analysis(step_sizes, [conn_def_alpha, conn_def_velocity, conn_def_torque], sequences, 'linear', 'linear', ['Alpha defect','Velocity defect','Torque defect' ])
   


if __name__ == '__main__':
    plot_signals()
    # residual_analysis()
