from JumpScale import j


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
    node = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])

    node_client = j.clients.g8core.get(host=node.model.data.redisAddr,
                                       port=node.model.data.redisPort,
                                       password=node.model.data.redisPassword)
    mgmtaddr, network = getMgmtInfo(job, node, node_client)
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
    this method will be called from the node.g8os install action.
    """
    import netaddr

    node = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])
    job.logger.info("execute network configure on {}".format(node))

    node_client = j.clients.g8core.get(host=node.model.data.redisAddr,
                                       port=node.model.data.redisPort,
                                       password=node.model.data.redisPassword)

    service = job.service

    mgmtaddr, network = getMgmtInfo(job, node, node_client)

    storageaddr = combine(str(network.ip), mgmtaddr, network.prefixlen)
    vxaddr = combine('10.240.0.0', mgmtaddr, network.prefixlen)

    node_client.timeout = 120
    nics = node_client.info.nic()
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

    containers = node_client.container.find('ovs')
    if containers:
        ovs_container_id = int(list(containers)[0])
    else:
        ovs_container_id = int(node_client.container.create('https://hub.gig.tech/gig-official-apps/ovs.flist', host_network=True, tags=['ovs']).get(360).data)
    container_client = node_client.container.client(ovs_container_id)
    container_client.json('ovs.bridge-add', {"bridge": "backplane"})
    container_client.json('ovs.port-add', {"bridge": "backplane", "port": interface, "vlan": 0})
    node_client.system('ip address add {addr}/{subnet} dev backplane'.format(addr=storageaddr, sunbet=network.prefixlen))
    container_client.json('ovs.vlan-ensure', {'master': 'backplane', 'vlan': service.model.data.vlanTag, 'name': 'vxbackend'})
    node_client.system('ip address add {addr}/{subnet} dev vxbackend'.format(addr=vxaddr, subnet=network.prefixlen))

    service.model.data.vxaddr = vxaddr
    service.model.data.storageaddr = storageaddr
    service.model.data.subnet = network.prefixlen
    service.saveall()
