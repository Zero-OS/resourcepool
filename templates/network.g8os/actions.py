def combine(ip1, ip2, mask):
    """
    >>> combine('10.0.3.11', '192.168.1.10', 24)
    '10.0.3.10'
    """
    import netaddr
    iip1 = netaddr.IPNetwork('{}/{}'.format(ip1, mask))
    iip2 = netaddr.IPNetwork('{}/{}'.format(ip2, mask))
    ires = iip1.network + int(iip2.ip & (~ int(iip2.netmask)))
    return ires.format()


def configure(job):
    """
    this method will be called from the node.g8os install action.
    """

    # if 'node' not in job.model.args:
    #     raise ValueError("argument node not present in job argument")

    node = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])
    job.logger.info("execute network configure on {}".format(node))

    service = job.service

    net, mask = service.model.data.cidr.split('/')
    mgmtaddr = node.model.data.redisAddr

    storageaddr = combine(net, mgmtaddr, int(mask))
    vxaddr = combine('10.240.0.0', mgmtaddr, int(mask))

    node_client = j.clients.g8core.get(host=node.model.data.redisAddr,
                                       port=node.model.data.redisPort,
                                       password=node.model.data.redisPassword)

    node_client.timeout = 120
    nics = node_client.info.nic()
    nics.sort(key=lambda nic: nic['speed'])
    interface = None
    for nic in nics:
        if any(addr['addr'].startswith(mgmtaddr + '/') for addr in nic['addrs'] if 'addr' in addr):
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
    node_client.system('ip address add {addr}/{mask} dev backplane'.format(addr=storageaddr, mask=mask))
    container_client.json('ovs.vlan-ensure', {'master': 'backplane', 'vlan': service.model.data.vlanTag, 'name': 'vxbackend'})
    node_client.system('ip address add {addr}/{mask} dev vxbackend'.format(addr=vxaddr, mask=mask))
