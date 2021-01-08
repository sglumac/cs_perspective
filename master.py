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


def run(fmu, connections, dt, tEnd, sequence=None):
    """
    Run the 
    Gauss-Seidel (sequence = ordered list of instance names)
    or
    Jacobi (sequence=None)
    type co-simulation
    """
    slaves = {
        name: load_fmu(name, fmu['archivePath'])
        for name, fmu in fmus
    }

    for slave in slaves.values():
        slave.instantiate()
        slave.setupExperiment(startTime=0.)
        slave.enterInitializationMode()
        slave.exitInitializationMode()

 
    values = dict()
    for name, slave in slaves.items():
        for y in _outputs(slave):
            values[name, y] = [(0., slave.get(y)[0])]

    t = 0.
    while t < tEnd:
        for name in sequence:
            slave = slaves[name]
            for u in inputs(slave):
                s, y = connections[name, u]
                v = slaves[s].get(y)
                slave.set(u, v)

            slave.do_step(t0, dt, pyfmi.fmi.FMI2_TRUE)

            for y in outputs(slave):
                v = slave.get(y)
                values[name, y].append((t + dt, v[0]))
        t = t + dt
                
    for signal in values:
        values[signal] = np.array(values[signal]).T

    return values