from os import path
import configuration
import master


def main():
    current_dir = path.dirname(path.abspath(__file__))
    fmu_dir = path.join(current_dir, 'FMUs')
    slaves, connections = configuration.read(fmu_dir, 'FMUsXML.xml')
    results = master.run(slaves, connections, 1e-1, 10.)
    print(results)


if __name__ == '__main__':
    main()
