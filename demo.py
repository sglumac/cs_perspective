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


def plot_signals():
    """Simple time plot of the signals in the graph"""
    sequences = {
        'Jacobi': None,
        'Gauss-Seidel 12': ['Alpha', 'Engine', 'Inertia'],
        'Gauss-Seidel 21': ['Alpha', 'Inertia', 'Engine']
    }
    slaves, connections = configuration.read(fmu_dir(), 'example.xml')
    results = {
        name: master.run(slaves, connections, 1e-1, 10., sequence)
        for name, sequence in sequences.items()
    }
    results['analytical'] = analytic.solution(10., 1e-1)

    for sequence in sequences:
        print(evaluation.total_power_residual(
            connections, results[sequence], ('Engine', 'velocity'), ('Inertia', 'torque')
        ))
    _, (axVelocity, axTorque) = plt.subplots(2, 1, sharex=True)
    for name, result in results.items():
        ts = result['step_size'] * np.arange(len(result['Inertia', 'velocity']))
        axVelocity.plot(ts, result['Inertia', 'velocity'], label=name)
        axTorque.plot(ts, result['Engine', 'torque'], label=name)

    axTorque.legend()
    plt.show()


if __name__ == '__main__':
    plot_signals()
