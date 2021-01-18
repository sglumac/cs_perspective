from typing import NamedTuple
from itertools import chain
import fmpy  # pylint: disable=import-error
from fmpy.fmi2 import FMU2Slave  # pylint: disable=import-error
from fmpy.model_description import ModelDescription  # pylint: disable=import-error


Slave = NamedTuple('Slave', [
    ('description', ModelDescription), ('fmu', FMU2Slave)
])


def load_fmu(instance_name, path):
    """A function to read an FMU and go through default initialization"""

    mdl_desc = fmpy.read_model_description(path)
    unzip_dir = fmpy.extract(path)

    fmu = FMU2Slave(
        instanceName=instance_name,
        guid=mdl_desc.guid,
        modelIdentifier=mdl_desc.coSimulation.modelIdentifier,
        unzipDirectory=unzip_dir
    )
    return Slave(mdl_desc, fmu)


def _filter_mvs(mvs, causality):
    return {v.name: v.valueReference for v in mvs if v.causality == causality}


def _outputs(slave):
    return _filter_mvs(slave.description.modelVariables, 'output')


def _inputs(slave):
    return _filter_mvs(slave.description.modelVariables, 'input')


def _parameters(slave):
    return _filter_mvs(slave.description.modelVariables, 'parameter')


def run(slaves, connections, dt, tEnd, sequence=None, parameters=None):
    """
    Run the 
    Gauss-Seidel (sequence = ordered list of instance names)
    or
    Jacobi (sequence=None)
    type co-simulation
    """
    for name, slave in slaves.items():
        slave.fmu.instantiate()
        slave.fmu.setupExperiment(startTime=0.)
        slave.fmu.enterInitializationMode()
        if parameters and name in parameters:
            parameter_vars = _parameters(slave)
            refs_vals = dict(
                (parameter_vars[parameter], value)
                for parameter, value in parameters[name].items()
            )
            slave.fmu.setReal(refs_vals.keys(), [float(num) for num in refs_vals.values()])

    initialized = False
    while not initialized:
        initialized = True
        for (su, u), (sy, y) in connections.items():
            input_vars = _inputs(slaves[su])
            output_vars = _outputs(slaves[sy])
            out_val = slaves[sy].fmu.getReal([output_vars[y]])[0]
            input_val = slaves[su].fmu.getReal([input_vars[u]])[0]
            if input_val != out_val:
                slaves[su].fmu.setReal([input_vars[u]], [out_val])
                initialized = False

    for slave in slaves.values():
        slave.fmu.exitInitializationMode()
 
    results = {
        (name, port): []
        for name in slaves.keys()
        for port in chain(_inputs(slaves[name]), _outputs(slaves[name]))
    }

    def update_inputs(name, slave):
        input_vars = _inputs(slave)
        input_vals = dict()
        for u in input_vars.keys():
            val_ref = input_vars[u]
            s, y = connections[name, u]
            out_vars = _outputs(slaves[s])
            input_vals[val_ref] = slaves[s].fmu.getReal([out_vars[y]])[0]
        slave.fmu.setReal(input_vals.keys(), input_vals.values())
        for var, val_ref in input_vars.items():
            results[name, var].append(input_vals[val_ref])

    def read_outputs(name, slave, t):
        out_vars = _outputs(slave)
        out_vals = slave.fmu.getReal(out_vars.values())
        for port, val in zip(out_vars.keys(), out_vals):
            results[name, port].append(val)

    for name, slave in slaves.items():
        read_outputs(name, slave, 0.)
    for name, slave in slaves.items():
        update_inputs(name, slave)

    t = 0.
    while t < tEnd:
        if sequence:
            for name in sequence:
                slave = slaves[name]
                update_inputs(name, slave)
                slave.fmu.doStep(t, dt)
                read_outputs(name, slave, t + dt)
        else:
            for name, slave in slaves.items():
                update_inputs(name, slave)
            for name, slave in slaves.items():
                slave.fmu.doStep(t, dt)
                read_outputs(name, slave, t + dt)

        t = t + dt

    for slave in slaves.values():
        slave.fmu.terminate()

    return results
