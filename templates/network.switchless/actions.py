from js9 import j


def configure(job):
    """
    this method will be called from the node.zero-os install action.
    """
    import netaddr
    from zeroos.orchestrator.configuration import get_configuration, get_jwt_token
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.Container import Container

    nodeservice = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])
    job.logger.info("execute network configure on {}".format(nodeservice))

    node = Node.from_ays(nodeservice)
    service = job.service

    network = netaddr.IPNetwork(service.model.data.cidr)

    addresses = node.network.get_addresses(network)

    actor = service.aysrepo.actorGet("container")
    config = get_configuration(service.aysrepo)
    args = {
        'node': node.name,
        'hostname': 'ovs',
        'flist': config.get('ovs-flist', 'https://hub.gig.tech/gig-official-apps/ovs.flist'),
        'hostNetworking': True,
        'privileged': True,
    }
    cont_service = actor.serviceCreate(instance='{}_ovs'.format(node.name), args=args)
    job.context['token'] = get_jwt_token(job.service.aysrepo)
    j.tools.async.wrappers.sync(cont_service.executeAction('install', context=job.context))
    container_client = Container.from_ays(cont_service).client
    nics = node.client.info.nic()
    nicmap = {nic['name']: nic for nic in nics}
    freenics = node.network.get_free_nics()
    if not freenics:
        raise j.exceptions.RuntimeError("Could not find available nic")

    # freenics = ([1000, ['eth0']], [100, ['eth1']])
    for speed, nics in freenics:
        if len(nics) >= 2:
            break
    else:
        raise j.exceptions.RuntimeError("Could not find two equal available nics")

    if 'backplane' not in nicmap:
        container_client.json('ovs.bridge-add', {"bridge": "backplane", "options": {'stp_enable': 'true'}})
        container_client.json('ovs.port-add', {"bridge": "backplane", "port": nics[0], "vlan": 0})
        container_client.json('ovs.port-add', {"bridge": "backplane", "port": nics[1], "vlan": 0})
        node.client.system('ip address add {storageaddr} dev backplane'.format(**addresses)).get()
        node.client.system('ip link set dev {} mtu 2000'.format(nics[0])).get()
        node.client.system('ip link set dev {} mtu 2000'.format(nics[1])).get()
        node.client.system('ip link set dev backplane up').get()
    if 'vxbackend' not in nicmap:
        container_client.json('ovs.vlan-ensure', {'master': 'backplane', 'vlan': service.model.data.vlanTag, 'name': 'vxbackend'})
        node.client.system('ip address add {vxaddr} dev vxbackend'.format(**addresses)).get()
        node.client.system('ip link set dev vxbackend mtu 2000').get()
        node.client.system('ip link set dev vxbackend up').get()
