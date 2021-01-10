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
    return slaves, connections, sequences


def run_simulations(slaves, connections, sequences, step_size):
    """
    Runs co-simulations and the analytical calculation for the give step size.
    """
    results = {
        name: master.run(slaves, connections, step_size, 10., sequence)
        for name, sequence in sequences.items()
    }
    return results, analytic.solution(10., step_size)


def plot_signals():
    """Simple time plot of the signals in the graph"""
    slaves, connections, sequences = co_simulations()
    results, analytical = run_simulations(slaves, connections, sequences, 1e-1)
    results['analytical'] = analytical

    _, (axVelocity, axTorque) = plt.subplots(2, 1, sharex=True)
    for name, result in results.items():
        ts = result['step_size'] * np.arange(len(result['Inertia', 'velocity']))
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
    torque_errors = []
    velocity_errors = []
    tot_pow_residuals = []
    for step_size in step_sizes:
        results, analytical = run_simulations(slaves, connections, sequences, step_size)
        tot_pow_residuals.append(
            evaluation.total_power_residual(
                connections, results,
                ('Inertia', 'torque'), ('Engine', 'velocity')
            )
        )
        err = evaluation.global_error(connections, results)
        torque_errors.append(err['Engine', 'torque'])
        velocity_errors.append(err['Inertia', 'velocity'])

    _, (axTotPowResidual, axTorqueErr, axVelErr) = plt.subplots(3, 1, sharex=True)
    axTotPowResidual.plot(step_size)


if __name__ == '__main__':
    plot_signals()
