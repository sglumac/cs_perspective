import numpy as np


def connection_defects(connections, results):
    """
    The connection defects of the given co-simulation network
    assuming zero-order hold
    """
    defects = {
        (su, u): np.array(results[su, u]) - results[sy, y]
        for (su, u), (sy, y) in connections.items()
    }
    defects['step_size'] = results['step_size']
    return defects


def total_power_residual(connections, results, effort_port, flow_port):
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
    return results['step_size'] * np.cumsum(np.abs(power_residual))[-1]


