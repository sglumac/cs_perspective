from os import path
import matplotlib.pyplot as plt
import numpy as np
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
        name: master.run(slaves, connections, step_size, tEnd, sequence)
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


def residual_analysis():
    """
    The analysis of total power residual and its comparison to the global error.
    """
    slaves, connections, sequences = co_simulations()
    step_sizes = [1 / den for den in 2 ** np.arange(1, 10)]
    torque_errors = {sequence: [] for sequence in sequences}
    velocity_errors = {sequence: [] for sequence in sequences}
    tot_pow_residuals = {sequence: [] for sequence in sequences} 
    GS_torque_error_subtract = [ 0 for i in range(len(step_sizes)) ]  #init array
    GS_velocity_error_subtract = [ 0 for i in range(len(step_sizes)) ]  #init array
    for step_size in step_sizes:
        results, analytic = run_simulations(slaves, connections, sequences, step_size)
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
        GS_torque_error_subtract[int(step_size)] = torque_errors['Gauss-Seidel 12'][int(step_size)] - torque_errors['Gauss-Seidel 21'][int(step_size)]
        GS_velocity_error_subtract[int(step_size)] = velocity_errors['Gauss-Seidel 12'][int(step_size)] - velocity_errors['Gauss-Seidel 21'][int(step_size)]

    _, axs = plt.subplots(3, 1, sharex=True)
    axTotPowResidual, axTorqueErr, axVelErr = axs

    for sequence in sequences:
        axTotPowResidual.plot(step_sizes, tot_pow_residuals[sequence], label=sequence)
        axTorqueErr.plot(step_sizes, torque_errors[sequence], label=sequence)
        axVelErr.plot(step_sizes, velocity_errors[sequence], label=sequence)
    axTotPowResidual.set_title('Total power residual')
    axTorqueErr.set_title('Torque global error')
    axVelErr.set_title('Velocity global error')

    for ax in axs:
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.legend()
    plt.show()
    
    fig = plt.figure(2)
    ax = fig.add_subplot(2, 1, 1)
    plt.plot(step_sizes, GS_torque_error_subtract, label = 'trq GS12 - GS21')
    ax.set_xscale('log')
    plt.legend()
    ax.set_title('GS12 - GS21 torque subtraction')
    plt.subplot(212)
    ax2 = fig.add_subplot(2, 1, 2)
    plt.plot(step_sizes, GS_velocity_error_subtract, label = 'vel GS12 - GS21')
    ax2.set_xscale('log')
    plt.legend()
    ax2.set_title('GS12 - GS21 velocity subtraction')
    plt.show()
    


if __name__ == '__main__':
    residual_analysis()
