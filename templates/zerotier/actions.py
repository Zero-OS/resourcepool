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

    client = _get_client(job)
    client.zerotier.join(job.service.model.data.nwid)

    def get_member():
        start = time.time()
        while start + 60 > time.time():
            resp = zerotier.network.getMember(address, job.service.model.data.nwid)
            if resp.content:
                return resp.json()
            time.sleep(0.5)
        raise j.exceptions.RuntimeError('Could not find member on zerotier network')

    token = job.service.model.data.token
    if token:
        address = client.zerotier.info()['address']
        zerotier = ztclient.Client()
        zerotier.set_auth_header('bearer {}'.format(token))

        member = get_member()
        if not member['config']['authorized']:
            # authorized new member
            job.logger.info("authorize new member {} to network {}".format(
                member['nodeId'], job.service.model.data.nwid))
            member['config']['authorized'] = True
            zerotier.network.updateMember(member, member['nodeId'], job.service.model.data.nwid)

    while True:
        net = _get_network(job)

        if (token and net['status'] == 'OK') or (not token and net['status'] in ['OK', 'ACCESS_DENIED']):
            break
        time.sleep(1)

    job.service.model.data.allowDefault = net['allowDefault']
    job.service.model.data.allowGlobal = net['allowGlobal']
    job.service.model.data.allowManaged = net['allowManaged']
    job.service.model.data.assignedAddresses = net['assignedAddresses']
    job.service.model.data.bridge = net['bridge']
    job.service.model.data.broadcastEnabled = net['broadcastEnabled']
    job.service.model.data.dhcp = net['dhcp']
    job.service.model.data.mac = net['mac']
    job.service.model.data.mtu = net['mtu']
    job.service.model.data.name = net['name']
    job.service.model.data.netconfRevision = net['netconfRevision']
    job.service.model.data.portDeviceName = net['portDeviceName']
    job.service.model.data.portError = net['portError']

    for route in net['routes']:
        if route['via'] is None:
            route['via'] = ''

    job.service.model.data.routes = net['routes']
    job.service.model.data.status = net['status']
    job.service.model.data.type = net['type'].lower()
    job.service.saveAll()


def delete(job):
    service = job.service
    client = _get_client(job)
    client.zerotier.leave(service.model.data.nwid)
