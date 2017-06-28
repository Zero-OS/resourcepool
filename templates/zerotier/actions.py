def _get_client(job, token):
    from zeroos.orchestrator.sal.Node import Node
    return Node.from_ays(job.service.parent, token).client


def _get_network(job, token):
    client = _get_client(job, token)
    for net in client.zerotier.list():
        if net['id'] == job.service.model.data.nwid:
            return net


def _update_model(job, network):
    job.service.model.data.allowDefault = network['allowDefault']
    job.service.model.data.allowGlobal = network['allowGlobal']
    job.service.model.data.allowManaged = network['allowManaged']
    job.service.model.data.assignedAddresses = network['assignedAddresses']
    job.service.model.data.bridge = network['bridge']
    job.service.model.data.broadcastEnabled = network['broadcastEnabled']
    job.service.model.data.dhcp = network['dhcp']
    job.service.model.data.mac = network['mac']
    job.service.model.data.mtu = network['mtu']
    job.service.model.data.name = network['name']
    job.service.model.data.netconfRevision = network['netconfRevision']
    job.service.model.data.portDeviceName = network['portDeviceName']
    job.service.model.data.portError = network['portError']

    for route in network['routes']:
        if route['via'] is None:
            route['via'] = ''

    job.service.model.data.routes = network['routes']
    job.service.model.data.status = network['status']
    job.service.model.data.type = network['type'].lower()
    job.service.saveAll()


def install(job):
    import time
    from zerotier import client as ztclient

    client = _get_client(job, job.context['token'])
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
        net = _get_network(job, job.context['token'])

        if (token and net['status'] == 'OK') or (not token and net['status'] in ['OK', 'ACCESS_DENIED']):
            break
        time.sleep(1)

    _update_model(job, net)


def delete(job):
    service = job.service
    client = _get_client(job, job.context['token'])
    client.zerotier.leave(service.model.data.nwid)


def monitor(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    if job.service.model.actionsState['install'] == 'ok':
        _update_model(job, _get_network(job,  get_jwt_token(job.service.aysrepo)))
