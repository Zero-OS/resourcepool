from js9 import j


def input(job):
    for required in['zerotierNetID', 'zerotierToken']:
        if not job.model.args.get(required):
            raise j.exceptions.Input("{} cannot be empty".format(required))

    return job.model.args


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


def delete_node(job):
    """
    this method will be called from the node.zero-os to remove the node from zerotier
    """
    from zerotier import client

    node = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])

    service = job.service
    token = service.model.data.zerotierToken
    netid = service.model.data.zerotierNetID

    zerotier = client.Client()
    zerotier.set_auth_header('bearer {}'.format(token))

    resp = zerotier.network.listMembers(netid)
    members = resp.json()

    for member in members:
        if node.model.data.redisAddr in member['config']['ipAssignments']:
            try:
                if member['config']['authorized']:
                    member['config']['authorized'] = False
                    zerotier.network.updateMember(member, member['nodeId'], netid)
            except Exception as err:
                job.logger.error(str(err))
            break


def try_authorize(service, logger, netid, member, zerotier):
    import time
    from zeroos.orchestrator.sal.Node import Node

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
    node = Node(zerotier_ip)
    node.client.testConnectionAttempts = 0
    node.client.timeout = 10
    for attempt in range(5):
        try:
            logger.info("connection to g8os with IP: {}".format(zerotier_ip))
            node.client.ping()
            break
        except:
            continue
    else:
        raise RuntimeError("can't connect, unauthorize member IP: {}".format(zerotier_ip))

    # create node.zero-os service
    name = node.name
    try:
        node = service.aysrepo.serviceGet(role='node', instance=name)
        logger.info("service for node {} already exists, updating model".format(name))
        # mac sure the service has the correct ip in his model.
        # it could happend that a node get a new ip after a reboot
        node.model.data.redisAddr = zerotier_ip
        node.model.data.status = 'running'
        # after reboot we also wonna call install
        j.tools.async.wrappers.sync(node.executeAction('install'))
    except j.exceptions.NotFound:
        # create and install the node.zero-os service
        node_actor = service.aysrepo.actorGet('node.zero-os')
        networks = [n.name for n in service.producers.get('network', [])]

        node_args = {
            'id': name,
            'status': 'running',
            'networks': networks,
            'hostname': node.client.info.os()['hostname'],
            'redisAddr': zerotier_ip,
        }
        logger.info("create node.zero-os service {}".format(name))
        node = node_actor.serviceCreate(instance=name, args=node_args)
        try:

            logger.info("install node.zero-os service {}".format(name))
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
