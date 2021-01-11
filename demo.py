from os import path
import matplotlib.pyplot as plt
import numpy as np
import configuration
import master
import analytic
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
    return results, analytic.solution(step_size, tEnd)


def plot_signals():
    """Simple time plot of the signals in the graph"""
    slaves, connections, sequences = co_simulations()
    step_size = 1e-1
    results, analytical  = run_simulations(slaves, connections, sequences, step_size)
    results['analytical'] = analytical

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
    for step_size in step_sizes:
        results, analytical = run_simulations(slaves, connections, sequences, step_size)
        for sequence in sequences:
            tot_pow_residuals[sequence].append(
                evaluation.total_power_residual(
                    connections, results[sequence], step_size,
                    ('Inertia', 'torque'), ('Engine', 'velocity')
                )
            )
            errs = evaluation.global_error(results[sequence], analytical, step_size)
            torque_errors[sequence].append(errs['Engine', 'torque'])
            velocity_errors[sequence].append(errs['Inertia', 'velocity'])

    _, (axTotPowResidual, axTorqueErr, axVelErr) = plt.subplots(3, 1, sharex=True)
    axTotPowResidual.plot(step_size)


if __name__ == '__main__':
    plot_signals()
