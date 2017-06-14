from js9 import j


def combine(ip1, ip2, mask):
    """
    >>> combine('10.0.3.11', '192.168.1.10', 24)
    '10.0.3.10'
    """
    import netaddr
    iip1 = netaddr.IPNetwork('{}/{}'.format(ip1, mask))
    iip2 = netaddr.IPNetwork('{}/{}'.format(ip2, mask))
    ires = iip1.network + int(iip2.ip & (~ int(iip2.netmask)))
    net = netaddr.IPNetwork(ires)
    net.prefixlen = mask
    return net


def getAddresses(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    node = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])

    # @TODO ASK JO
    node_client = Node.from_ays(node, get_jwt_token(job.service.aysrepo))
    mgmtaddr, network = getMgmtInfo(job, node, node_client.client)
    return {
        'storageaddr': combine(str(network.ip), mgmtaddr, network.prefixlen),
        'vxaddr': combine('10.240.0.0', mgmtaddr, network.prefixlen),
    }


def getMgmtInfo(job, node, node_client):
    import netaddr

    def get_nic_ip(nics, name):
        for nic in nics:
            if nic['name'] == name:
                for ip in nic['addrs']:
                    return netaddr.IPNetwork(ip['addr'])
                return

    service = job.service

    network = netaddr.IPNetwork(service.model.data.cidr)
    defaultgwdev = node_client.bash("ip route | grep default | awk '{print $5}'").get().stdout.strip()
    nics = node_client.info.nic()
    mgmtaddr = None
    if defaultgwdev:
        ipgwdev = get_nic_ip(nics, defaultgwdev)
        if ipgwdev:
            mgmtaddr = str(ipgwdev.ip)
    if not mgmtaddr:
        mgmtaddr = node.model.data.redisAddr

    return mgmtaddr, network


def configure(job):
    """
    this method will be called from the node.zero-os install action.
    """
    import netaddr
    from zeroos.orchestrator.configuration import get_configuration, get_jwt_token
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.Container import Container

    node = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])
    job.logger.info("execute network configure on {}".format(node))

    # @TODO ASK JO
    node_client = Node.from_ays(node, get_jwt_token(job.service.aysrepo))
    service = job.service

    mgmtaddr, network = getMgmtInfo(job, node, node_client.client)

    storageaddr = combine(str(network.ip), mgmtaddr, network.prefixlen)
    vxaddr = combine('10.240.0.0', mgmtaddr, network.prefixlen)

    nics = node_client.client.info.nic()
    nics.sort(key=lambda nic: nic['speed'])
    interface = None
    for nic in nics:
        # skip all interface that have an ipv4 address
        if any(netaddr.IPNetwork(addr['addr']).version == 4 for addr in nic['addrs'] if 'addr' in addr):
            continue
        if nic['speed'] == 0:
            continue
        interface = nic['name']
        break
    if interface is None:
        raise j.exceptions.RuntimeError("No interface available")

    actor = service.aysrepo.actorGet("container")
    config = get_configuration(service.aysrepo)
    args = {
        'node': node.name,
        'hostname': 'ovs',
        'flist': config.get('ovs-flist', 'https://hub.gig.tech/gig-official-apps/ovs.flist'),
        'hostNetworking': True,
    }
    cont_service = actor.serviceCreate(instance='{}_ovs'.format(node.name), args=args)
    j.tools.async.wrappers.sync(cont_service.executeAction('install'))
    # @TODO ASK JO
    container_client = Container.from_ays(cont_service, get_jwt_token(job.service.aysrepo)).client
    nicmap = {nic['name']: nic for nic in nics}
    if 'backplane' not in nicmap:
        container_client.json('ovs.bridge-add', {"bridge": "backplane"})
        container_client.json('ovs.port-add', {"bridge": "backplane", "port": interface, "vlan": 0})
        node_client.client.system('ip address add {addr} dev backplane'.format(addr=storageaddr)).get()
        node_client.client.system('ip link set dev backplane up').get()
    if 'vxbackend' not in nicmap:
        container_client.json('ovs.vlan-ensure', {'master': 'backplane', 'vlan': service.model.data.vlanTag, 'name': 'vxbackend'})
        node_client.client.system('ip address add {addr} dev vxbackend'.format(addr=vxaddr)).get()
        node_client.client.system('ip link set dev vxbackend up').get()
