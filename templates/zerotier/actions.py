def _get_client(job):
    from zeroos.orchestrator.sal.Node import Node
    return Node.from_ays(job.service.parent, job.context['token']).client


def _get_network(job):
    client = _get_client(job)
    for net in client.zerotier.list():
        if net['id'] == job.service.model.data.nwid:
            return net


def install(job):
    import time
    from zerotier import client as ztclient

    data = job.service.model.data
    client = _get_client(job)
    client.zerotier.join(data.nwid)

    def get_member():
        start = time.time()
        while start + 60 > time.time():
            resp = zerotier.network.getMember(address, data.nwid)
            if resp.content:
                return resp.json()
            time.sleep(0.5)
        raise j.exceptions.RuntimeError('Could not find member on zerotier network')

    if data.token:
        address = client.zerotier.info()['address']
        zerotier = ztclient.Client()
        zerotier.set_auth_header('bearer {}'.format(data.token))

        member = get_member()
        if not member['config']['authorized']:
            # authorized new member
            job.logger.info("authorize new member {} to network {}".format(member['nodeId'], data.nwid))
            member['config']['authorized'] = True
            zerotier.network.updateMember(member, member['nodeId'], data.nwid)

    while True:
        net = _get_network(job)
        if net['status'] == 'OK':
            break
        time.sleep(1)
    data.allowDefault = net['allowDefault']
    data.allowGlobal = net['allowGlobal']
    data.allowManaged = net['allowManaged']
    data.allowDefault = net['allowDefault']
    data.assignedAddresses = net['assignedAddresses']
    data.bridge = net['bridge']
    data.broadcastEnabled = net['broadcastEnabled']
    data.dhcp = net['dhcp']
    data.mac = net['mac']
    data.mtu = net['mtu']
    data.name = net['name']
    data.netconfRevision = net['netconfRevision']
    data.portDeviceName = net['portDeviceName']
    data.portError = net['portError']

    for route in net['routes']:
        if route['via'] is None:
            route['via'] = ''

    data.routes = net['routes']
    data.status = net['status']
    data.type = net['type'].lower()


def delete(job):
    service = job.service
    client = _get_client(job)
    client.zerotier.leave(service.model.data.nwid)
