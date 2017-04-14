from JumpScale import j

def is_valid_nic(nic):
    for exclude in ['zt', 'core', 'kvm', 'lo']:
        if nic['name'].startswith(exclude):
            return False
    return True

def bootstrap(job):
    from zerotier import client
    from  redis import ConnectionError
    import time

    service = job.service
    token = service.model.data.zerotierToken
    netid = service.model.data.zerotierNetID

    zerotier = client.Client()
    zerotier.set_auth_header('bearer {}'.format(token))


    resp = zerotier.network.listMembers(netid)
    members = resp.json()

    for member in members:
        if not member['online'] or member['config']['authorized']:
            continue

        # authorized new member
        job.logger.info("authorize new member {}".format(member['nodeId']))
        member['config']['authorized'] = True
        zerotier.network.updateMember(member, member['nodeId'], netid)

        # get assigned ip of this member
        resp = zerotier.network.getMember(member['nodeId'], netid)
        member = resp.json()
        while len(member['config']['ipAssignments']) <= 0:
            time.sleep(1)
            resp = zerotier.network.getMember(member['nodeId'], netid)
            member = resp.json()
        zerotier_ip = member['config']['ipAssignments'][0]

        # test if we can connect to the new member
        job.logger.info("connection to g8os with IP: {}".format(zerotier_ip))
        g8 = j.clients.g8core.get(zerotier_ip)
        g8.timeout = 10
        try:
            g8.ping()
        except:
            # can't connect, unauthorize member
            member['config']['authorized'] = False
            zerotier.network.updateMember(member, member['nodeId'], netid)

        # read mac Addr of g8os
        mac = None
        try:
            for nic in filter(is_valid_nic, g8.info.nic()):
                # get mac address and ip of the management interface
                if len(nic['addrs']) > 0 and nic['addrs'][0]['addr'] != '':
                    mac = nic['hardwareaddr']
                    break
        except ConnectionError:
            j.logger.error("can't connect to g8os at {}".format(zerotier_ip))
            continue

        if mac is None:
            j.logger.error("can't find mac address of the zerotier member ({})".format(member['physicalAddress']))
            continue

        # create node.g8os service
        mac = mac.replace(':', '')
        try:
            node = service.aysrepo.serviceGet(role='node', instance=mac)
            job.logger.info("service for node {} already exists, updating model".format(mac))
            # mac sure the service has the correct ip in his model.
            # it could happend that a node get a new ip after a reboot
            node.model.data.redisAddr = zerotier_ip
            node.model.data.status = 'running'

        except j.exceptions.NotFound:
            # create and install the node.g8os service
            node_actor = job.service.aysrepo.actorGet('node.g8os')
            networks = [n.name for n in service.producers.get('network', [])]

            node_args = {
                'id': mac,
                'status':'running',
                'networks': networks,
                'redisAddr': zerotier_ip,
            }
            job.logger.info("create node.g8os service {}".format(mac))
            node = node_actor.serviceCreate(instance=mac, args=node_args)

            job.logger.info("install node.g8os service {}".format(mac))
            j.tools.async.wrappers.sync(node.executeAction('install'))
