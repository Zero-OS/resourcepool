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

    # First make sure all members that need to be authorzed anyway, are authorized
    to_process = list()
    for member in members:
        if member['nodeId'] in service.model.data.authorizedZerotierMembers:
            if not member['config']['authorized']:
                job.logger.info("Authorizing %s" % member['nodeId'])
                member['config']['authorized'] = True
                zerotier.network.updateMember(member, member['nodeId'], netid)
        else:
            to_process.append(member)

    # In a second pass process all the others
    for member in to_process:
        try:
            try_authorize(job, job.logger, netid, member, zerotier)
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
                zerotier.network.deleteMember(member['nodeId'], netid)
            except Exception as err:
                job.logger.error(str(err))
            break


def try_authorize(job, logger, netid, member, zerotier):
    import time
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    job.context['token'] = get_jwt_token(service.aysrepo)

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
    node = Node(zerotier_ip, password=get_jwt_token(service.aysrepo))
    node.client.testConnectionAttempts = 0
    node.client.timeout = 30
    for attempt in range(5):
        try:
            logger.info("connection to g8os with IP: {}".format(zerotier_ip))
            node.client.ping()
            break
        except:
            continue
    else:
        raise RuntimeError("can't connect, unauthorize member IP: {}".format(zerotier_ip))

    # connection succeeded, set the hostname of the node to zerotier member
    member['name'] = node.name
    member['description'] = node.client.info.os().get('hostname', '')
    zerotier.network.updateMember(member, member['nodeId'], netid)

    # create node.zero-os service
    name = node.name
    try:
        nodeservice = service.aysrepo.serviceGet(role='node', instance=name)
        logger.info("service for node {} already exists, updating model".format(name))
        # mac sure the service has the correct ip in his model.
        # it could happend that a node get a new ip after a reboot
        nodeservice.model.data.redisAddr = zerotier_ip
        nodeservice.model.data.status = 'running'
        # after reboot we also wonna call install
        nodeservice.executeAction('install', context=job.context)
    except j.exceptions.NotFound:
        # do hardwarechecks
        for prod in service.producers.get('hardwarecheck', []):
            prod.executeAction('check', args={'ipaddr': zerotier_ip,
                                              'node_id': member['nodeId'],
                                              'jwt': get_jwt_token(service.aysrepo)})
        # create and install the node.zero-os service
        if service.model.data.wipedisks:
            node.wipedisks()

        node_actor = service.aysrepo.actorGet('node.zero-os')
        networks = [n.name for n in service.producers.get('network', [])]

        hostname = node.client.info.os()['hostname']
        if hostname == 'zero-os':
            hostname = 'zero-os-%s' % name

        node_args = {
            'id': name,
            'status': 'running',
            'networks': networks,
            'hostname': hostname,
            'redisAddr': zerotier_ip,
        }
        logger.info("create node.zero-os service {}".format(name))
        nodeservice = node_actor.serviceCreate(instance=name, args=node_args)
        try:

            logger.info("install node.zero-os service {}".format(name))
            nodeservice.executeAction('install', context=job.context)
        except:
            nodeservice.delete()
            raise

    # do ERP registrations
    for prod in service.producers.get('erp_registration', []):
        prod.executeAction('register', args={'node_id': name, 'zerotier_address': member['nodeId']})


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


def monitor(job):
    pass
