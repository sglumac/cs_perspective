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


def residual_analysis():
    """
    The analysis of total power residual and its comparison to the global error.
    """
    slaves, connections, sequences = co_simulations()
    step_sizes = [1 / den for den in 2 ** np.arange(1, 10)]
    torque_errors = {sequence: [] for sequence in sequences}
    velocity_errors = {sequence: [] for sequence in sequences}
    tot_pow_residuals = {sequence: [] for sequence in sequences} 
    #engine_power = {sequence: [] for sequence in sequences}
    #inertia_power = {sequence: [] for sequence in sequences}
    engine_power_errors = {sequence: [] for sequence in sequences}
    inertia_power_errors = {sequence: [] for sequence in sequences}
    power_errors = {sequence: [] for sequence in sequences}
    conn_def_alpha = {sequence: [] for sequence in sequences}
    conn_def_velocity = {sequence: [] for sequence in sequences}
    conn_def_torque = {sequence: [] for sequence in sequences}
    engineAnalytic_power = []
    inertiaAnalytic_power = []

    for step_size in step_sizes:
        results, analytic = run_simulations(slaves, connections, sequences, step_size)
        #engineAnalytic_power.append(step_size * np.cumsum(np.abs(np.array(list(analytic['Engine','torque']))*list(analytic['Engine','velocity'])))[-1])
        #inertiaAnalytic_power.append(step_size * np.cumsum(np.abs(np.array(list(analytic['Inertia','torque']))*list(analytic['Inertia','velocity'])))[-1])
        engineAnalytic_power = np.array(analytic['Engine','torque'])*analytic['Engine','velocity']
        inertiaAnalytic_power = np.array(analytic['Inertia','torque'])*analytic['Inertia','velocity']
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
            
            #engine_power[sequence].append(step_size * np.cumsum(np.abs(np.array(list(results[sequence]['Engine','torque']))*list(results[sequence]['Engine','velocity'])))[-1])
            #inertia_power[sequence].append(step_size * np.cumsum(np.abs(np.array(list(results[sequence]['Inertia','torque']))*list(results[sequence]['Inertia','velocity'])))[-1])
            engine_power = np.array(results[sequence]['Engine','torque'])*results[sequence]['Engine','velocity']
            inertia_power = np.array(results[sequence]['Inertia','torque'])*results[sequence]['Inertia','velocity']            
            power = np.array(results[sequence]['Engine','torque'])*results[sequence]['Inertia','velocity']
            
            engine_power_errors[sequence].append(step_size*np.cumsum( np.abs(engine_power - engineAnalytic_power) )[-1])  
            inertia_power_errors[sequence].append(step_size*np.cumsum( np.abs(inertia_power - inertiaAnalytic_power) )[-1])
            power_errors[sequence].append(step_size*np.cumsum( np.abs(power - Analytic_power) )[-1])
            
            input_defect = evaluation.connection_defects(connections, results[sequence])
            conn_def_alpha[sequence].append( step_size*np.cumsum( np.abs(input_defect['Engine', 'alpha']))[-1] )
            conn_def_velocity[sequence].append( step_size*np.cumsum( np.abs(input_defect['Engine', 'velocity']))[-1] )
            conn_def_torque[sequence].append( step_size*np.cumsum( np.abs(input_defect['Inertia', 'torque']))[-1] )

    GS_torque_error_subtract = [
        gs12 - gs21 for gs12, gs21 in zip(torque_errors['Gauss-Seidel 12'], torque_errors['Gauss-Seidel 21'])
    ]
    GS_velocity_error_subtract = [
        gs12 - gs21 for gs12, gs21 in zip(velocity_errors['Gauss-Seidel 12'], velocity_errors['Gauss-Seidel 21'])
    ]

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
    
    fig = plt.figure(3)
    ax = fig.add_subplot(2, 1, 1)
    for sequence in sequences:
        plt.plot(step_sizes, engine_power_errors[sequence], label = sequence)
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.legend()
    ax.set_title('Engine power error')
    ax2 = fig.add_subplot(2, 1, 2)
    for sequence in sequences:
        plt.plot(step_sizes, inertia_power_errors[sequence], label = sequence)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    plt.legend()
    ax2.set_title('Inertia power error')    
    plt.show()
    
    fig = plt.figure(4)
    ax = fig.add_subplot(1, 1, 1)
    for sequence in sequences:
        plt.plot(step_sizes, power_errors[sequence], label = sequence)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title('Power error')
    plt.legend()
    plt.show()
    
    fig = plt.figure(5)
    ax = fig.add_subplot(3, 1, 1)
    for sequence in sequences:
        plt.plot(step_sizes, conn_def_alpha[sequence], label = sequence)
    ax.set_title('Alpha defect')
    plt.legend()
    ax = fig.add_subplot(3, 1, 2)
    for sequence in sequences:
        plt.plot(step_sizes, conn_def_velocity[sequence], label = sequence)
    ax.set_title('Velocity defect')
    plt.legend()
    ax = fig.add_subplot(3, 1, 3)
    for sequence in sequences:
        plt.plot(step_sizes, conn_def_torque[sequence], label = sequence)
    ax.set_title('Torque defect')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    plot_signals()
    #residual_analysis()
