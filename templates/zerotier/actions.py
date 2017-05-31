def _get_client(parent):
    from zeroos.orchestrator.sal.Node import Node
    return Node.from_ays(parent).client


def _get_network(service):
    client = _get_client(service.parent)
    for net in client.zerotier.list():
        if net['id'] == service.model.data.nwid:
            return net


def install(job):
    import time
    service = job.service
    client = _get_client(service.parent)
    client.zerotier.join(service.model.data.nwid)

    while True:
        net = _get_network(service)
        if net['status'] == 'OK':
            break
        time.sleep(1)
    service.model.data.allowDefault = net['allowDefault']
    service.model.data.allowGlobal = net['allowGlobal']
    service.model.data.allowManaged = net['allowManaged']
    service.model.data.allowDefault = net['allowDefault']
    service.model.data.assignedAddresses = net['assignedAddresses']
    service.model.data.bridge = net['bridge']
    service.model.data.broadcastEnabled = net['broadcastEnabled']
    service.model.data.dhcp = net['dhcp']
    service.model.data.mac = net['mac']
    service.model.data.mtu = net['mtu']
    service.model.data.name = net['name']
    service.model.data.netconfRevision = net['netconfRevision']
    service.model.data.portDeviceName = net['portDeviceName']
    service.model.data.portError = net['portError']

    for route in net['routes']:
        if route['via'] is None:
            route['via'] = ''

    service.model.data.routes = net['routes']
    service.model.data.status = net['status']
    service.model.data.type = net['type'].lower()


def delete(job):
    service = job.service
    client = _get_client(service.parent)
    client.zerotier.leave(service.model.data.nwid)
