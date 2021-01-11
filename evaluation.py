import numpy as np


def connection_defects(connections, results):
    """
    The connection defects of the given co-simulation network
    assuming zero-order hold
    """
    defects = {
        u: np.array(results[u]) - results[y]
        for u, y in connections.items()
    }
    return defects


def total_power_residual(connections, results, step_size, effort_port, flow_port):
    """
    Calculates the total power residual for the power bond given
    with the input effort_port and the input flow_port.
    """
    defects = connection_defects(connections, results)
    effort_defect = defects[effort_port]
    flow_defect = defects[flow_port]
    effort = results[effort_port]
    flow = results[flow_port]
    power_residual = effort_defect * flow - effort * flow_defect
    return step_size * np.cumsum(np.abs(power_residual))[-1]


def global_error(results, analytical, step_size):
    """
    Calculates the global error of all the signals.
    """
    return {
        port: step_size * np.cumsum(np.abs(np.array(results[port]) - analytical[port]))[-1]
        for port, vals in results.items()
    }
