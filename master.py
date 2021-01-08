from typing import NamedTuple
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


def run(fmus, connections, dt, tEnd, sequence=None):
    """
    Run the 
    Gauss-Seidel (sequence = ordered list of instance names)
    or
    Jacobi (sequence=None)
    type co-simulation
    """
    slaves = {
        name: load_fmu(name, fmu['archivePath'])
        for name, fmu in fmus.items()
    }

    for _, fmu in slaves.values():
        fmu.instantiate()
        fmu.setupExperiment(startTime=0.)
        fmu.enterInitializationMode()
        fmu.exitInitializationMode()

 
    values = {(name, port): [] for name in slaves.keys() for port in _outputs(slaves[name])}

    def update_inputs(name, slave):
        input_vars = _inputs(slave)
        input_vals = dict()
        for u in input_vars.keys():
            val_ref = input_vars[u]
            s, y = connections[name, u]
            out_vars = _outputs(slaves[s])
            input_vals[val_ref] = slaves[s].fmu.getReal([out_vars[y]])[0]
        slave.fmu.setReal(input_vals.keys(), input_vals.values())

    def read_outputs(name, slave, t):
        for y in _outputs(slave):
            out_vars = _outputs(slave)
            out_vals = slave.fmu.getReal(out_vars.values())
            for port, val in zip(out_vars.keys(), out_vals):
                values[name, port].append((t, val))

    for name, slave in slaves.items():
        read_outputs(name, slave, 0.)

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

    return values