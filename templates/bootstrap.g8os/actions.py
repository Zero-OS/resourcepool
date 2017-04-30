from JumpScale import j

def input(job):
    for required in['zerotierNetID', 'zerotierToken']:
        if not job.model.args.get(required):
            raise j.exceptions.Input("{} cannot be empty".format(required))

    return job.model.args

def node_name(g8client):
    def get_nic_hwaddr(nics, name):
        for nic in nics:
            if nic['name'] == name:
                return nic['hardwareaddr']

    defaultgwdev = g8client.bash("ip route | grep default | awk '{print $5}'").get().stdout.strip()
    nics = g8client.info.nic()
    if defaultgwdev:
        macgwdev = get_nic_hwaddr(nics, defaultgwdev)
    if not macgwdev:
        raise AttributeError("name not find")
    return macgwdev.replace(":", '')

def bootstrap(job):
    from zerotier import client

    service = job.service
    token = service.model.data.zerotierToken
    netid = service.model.data.zerotierNetID

    zerotier = client.Client()
    zerotier.set_auth_header('bearer {}'.format(token))

    resp = zerotier.network.listMembers(netid)
    members = resp.json()

    for member in members:
        try:
            try_authorize(service, job.logger, netid, member, zerotier)
        except Exception as err:
            job.logger.error(str(err))
            member['config']['authorized'] = False
            zerotier.network.updateMember(member, member['nodeId'], netid)

def try_authorize(service, logger, netid, member, zerotier):
    import time

    if not member['online'] or member['config']['authorized']:
        return

    # authorized new member
    logger.info("authorize new member {}".format(member['nodeId']))
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
    g8 = j.clients.g8core.get(zerotier_ip)
    g8.timeout = 10
    for attempt in range(5):
        try:
            logger.info("connection to g8os with IP: {}".format(zerotier_ip))
            g8.ping()
            break
        except:
            continue
    else:
        raise RuntimeError("can't connect, unauthorize member IP: {}".format(zerotier_ip))

    # read mac Addr of g8os
    mac = node_name(g8)

    # create node.g8os service
    try:
        node = service.aysrepo.serviceGet(role='node', instance=mac)
        logger.info("service for node {} already exists, updating model".format(mac))
        # mac sure the service has the correct ip in his model.
        # it could happend that a node get a new ip after a reboot
        node.model.data.redisAddr = zerotier_ip
        node.model.data.status = 'running'

    except j.exceptions.NotFound:
        # create and install the node.g8os service
        node_actor = service.aysrepo.actorGet('node.g8os')
        networks = [n.name for n in service.producers.get('network', [])]

        node_args = {
            'id': mac,
            'status': 'running',
            'networks': networks,
            'redisAddr': zerotier_ip,
        }
        logger.info("create node.g8os service {}".format(mac))
        node = node_actor.serviceCreate(instance=mac, args=node_args)
        try:

            logger.info("install node.g8os service {}".format(mac))
            j.tools.async.wrappers.sync(node.executeAction('install'))
        except:
            j.tools.async.wrappers.sync(node.delete())
            raise

def processChange(job):
    service = job.service
    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema":
        ztID = job.model.args.get('zerotierNetID')
        if ztID:
            service.model.data.zerotierNetID = ztID
        token = job.model.args.get('zerotierToken')
        if token:
            service.model.data.zerotierToken = token
