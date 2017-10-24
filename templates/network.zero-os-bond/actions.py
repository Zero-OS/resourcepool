from js9 import j


def configure(job):
    """
    this method will be called from the node.zero-os install action.
    """
    import netaddr
    import time
    from zeroos.orchestrator.configuration import get_configuration, get_jwt_token
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.Container import Container

    nodeservice = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])
    job.logger.info("execute network configure on {}".format(nodeservice))

    node = Node.from_ays(nodeservice, get_jwt_token(job.service.aysrepo))
    service = job.service

    network = netaddr.IPNetwork(service.model.data.cidr)
    if service.model.data.driver:
        # we reload the driver because on some buggy hardware this is required
        node.client.system('modprobe -r {}'.format(service.model.data.driver)).get()
        devs = {link['name'] for link in node.client.ip.link.list()}
        node.client.system('modprobe {}'.format(service.model.data.driver)).get()
        alldevs = {link['name'] for link in node.client.ip.link.list()}
        driverdevs = alldevs - devs
        for link in driverdevs:
            node.client.ip.link.up(link)
        # wait max 10 seconds for these nics to become up (speed available)
        now = time.time()
        while time.time() - 10 < now:
            for nic in node.client.info.nic():
                if nic['speed'] and nic['name'] in driverdevs:
                    driverdevs.remove(nic['name'])
            if not driverdevs:
                break
            time.sleep(1)

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
    job.context['token'] = get_jwt_token(job.service.aysrepo)
    cont_service = actor.serviceCreate(instance='{}_ovs'.format(node.name), args=args)
    cont_service.executeAction('install', context=job.context)
    container_client = Container.from_ays(cont_service, get_jwt_token(job.service.aysrepo)).client
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
        container_client.json('ovs.bridge-add', {"bridge": "backplane"})
        container_client.json('ovs.bond-add', {"bridge": "backplane",
                                               "port": "bond0",
                                               "links": [nics[0], nics[1]],
                                               "lacp": True,
                                               "mode": "balance-tcp"})
        node.client.system('ip address add {storageaddr} dev backplane'.format(**addresses)).get()
        node.client.system('ip link set dev {} mtu 2000'.format(nics[0])).get()
        node.client.system('ip link set dev {} mtu 2000'.format(nics[1])).get()
        node.client.system('ip link set dev backplane up').get()
    if 'vxbackend' not in nicmap:
        container_client.json('ovs.vlan-ensure', {'master': 'backplane', 'vlan': service.model.data.vlanTag, 'name': 'vxbackend'})
        node.client.system('ip address add {vxaddr} dev vxbackend'.format(**addresses)).get()
        node.client.system('ip link set dev vxbackend mtu 2000').get()
        node.client.system('ip link set dev vxbackend up').get()
