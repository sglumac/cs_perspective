from lxml import etree

import os


def read(fmuDir, configurationFile):

    with open(os.path.join(fmuDir, 'configuration.xsd')) as f:
        schemaRoot = etree.XML(f.read())

    configSchema = etree.XMLSchema(schemaRoot)
    xmlParser = etree.XMLParser(schema=configSchema)

    with open(os.path.join(fmuDir, configurationFile), 'r') as f:
        tree = etree.fromstring(f.read(), xmlParser)

    slaves = dict()
    xmlInstances = tree.xpath('/Configuration/Instances/Instance')
    for instance in xmlInstances:
        instanceName = instance.attrib['instanceName']
        fmu = instance.xpath('Archive')[0].attrib['archiveName']
        instanceData = dict()
        instanceData['archivePath'] = os.path.join(fmuDir, fmu)
        instanceData['parameters'] = {p.attrib['name']: p.attrib['value'] for p in instance.xpath('Parameters/Parameter')}
        slaves[instanceName] = instanceData

    connections = dict()
    xmlConnections = tree.xpath('/Configuration/Connections/Connection')
    for connection in xmlConnections:
        source = connection.xpath('Source')[0]
        sy = source.attrib['instanceName']
        y = source.attrib['outputName']
        destination = connection.xpath('Destination')[0]
        su = destination.attrib['instanceName']
        u = destination.attrib['inputName']
        connections[su,u] = (sy,y)

    return slaves, connections
