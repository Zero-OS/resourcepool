def get_node_client(service):
    node = service.parent
    return j.clients.g8core.get(host=node.model.data.redisAddr,
                                port=node.model.data.redisPort,
                                password=node.model.data.redisPassword)

def create_container(service, parent):
    """
    first check if the volumes container for this vm exists.
    if not it creates it.
    return the container service
    """
    container_name = 'volumes_{}_{}'.format(service.name, parent.name)
    try:
        container = service.aysrepo.serviceGet(role='container', instance=container_name)
    except j.exceptions.NotFound:
        container = None

    if container is None:
        container_actor = service.aysrepo.actorGet('container')
        args = {
            'node': parent.name,
            'flist': 'https://hub.gig.tech/gig-official-apps/gonbdserver.flist',
            'hostNetworking': True,
            'storage': 'ardb://hub.gig.tech:16379',
        }
        container = container_actor.serviceCreate(instance=container_name, args=args)

    # make sure the container has the right parent, the node where this vm runs.
    container.model.changeParent(service.parent)

    return container

def create_nbd(service, container, volume):
    """
    first check if the nbd server for a specific volume exists.
    if not it creates it.
    return the nbdserver service
    """
    nbd_name = 'nbd_{}'.format(volume.name)

    try:
        nbdserver = service.aysrepo.serviceGet(role='container', instance=nbd_name)
    except j.exceptions.NotFound:
        nbdserver = None

    if nbdserver is None:
        nbd_actor = service.aysrepo.actorGet('nbdserver')
        args = {
            # 'backendControllerUrl': '', #FIXME
            # 'volumeControllerUrl': '', #FIXME
            'container': container.name,
        }
        nbdserver = nbd_actor.serviceCreate(instance=nbd_name, args=args)

    return nbdserver

def init(job):
    service = job.service

    # creates all nbd servers for each volume this vm uses
    job.logger.info("creates volumes container for vm {}".format(service.name))
    volume_container = create_container(service, service.parent)

    for volume in service.producers.get('volume', []):
        job.logger.info("creates nbd server for vm {}".format(service.name))
        nbdserver = create_nbd(service, volume_container, volume)
        service.consume(nbdserver)

def install(job):
    service = job.service

    # get all path to the vdisks serve by the nbdservers
    medias = []
    for nbdserver in service.producers.get('nbdserver', []):
        medias.append({'url': nbdserver.model.data.socketPath})
        # make sure the container is started
        j.tools.async.wrappers.sync(nbdserver.parent.executeAction('start'))
        # make sure the nbdserver is started
        j.tools.async.wrappers.sync(nbdserver.executeAction('start'))

    job.logger.info("create vm {}".format(service.name))
    client = get_node_client(service)
    client.experimental.kvm.create(
        service.name,
        media=medias,
        cpu=service.model.data.cpu,
        memory=service.model.data.memory,
        # port=None, #TODO
        # bridge=None #TODO
    )

    # TODO: test vm actually exists
    service.model.data.status = 'running'


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def stop(job):
    service = job.service


    for nbdserver in service.producers.get('nbdserver', []):
        job.logger.info("stop nbdserver for vm {}".format(service.name))
        # make sure the nbdserver is stopped
        j.tools.async.wrappers.sync(nbdserver.executeAction('stop'))

    job.logger.info("stop volumes container for vm {}".format(service.name))
    try:
        container_name = 'volumes_{}_{}'.format(service.name, service.parent.name)
        container = service.aysrepo.serviceGet(role='container', instance=container_name)
        j.tools.async.wrappers.sync(container.executeAction('stop'))
    except j.exceptions.NotFound:
        job.logger.info("container doesn't exists.")

    job.logger.info("stop vm {}".format(service.name))
    client = get_node_client(service)
    client.experimental.kvm.destroy(service.name)

    service.model.data.status = 'halted'

def pause(job):
    pass
    # raise NotADirectoryError()


def migrate(job):
    service = job.service

    service.model.data.status = 'migrating'

    args = job.model.args
    if 'node' not in args:
        raise j.exceptions.Input("migrate action expect to have the destination node in the argument")

    target_node = service.aysrepo.serviceGet('node', args['node'])
    job.logger.info("start migration of vm {} from {} to {}".format(service.name, service.parent.name, target_node.name))

    old_nbd = service.producers.get('nbdserver', [])
    container_name = 'volumes_{}_{}'.format(service.name, service.parent.name)
    old_volume_container = service.aysrepo.serviceGet('container', container_name)

    # start new nbdserver on target node
    volume_container = create_container(service, target_node)
    for volume in service.producers.get('volume', []):
        job.logger.info("start nbd server for migration of vm {}".format(service.name))
        nbdserver = create_nbd(service, volume_container, volume)
        service.consume(nbdserver)
        volume.model.data.node = target_node.name

    # TODO: migrate domain, not impleented yet in core0

    service.model.changeParent(target_node)
    service.model.data.status = 'running'

    # delete current nbd services and volue container
    job.logger.info("delete current nbd services and volume container")
    for nbdserver in old_nbd:
        j.tools.async.wrappers.sync(nbdserver.executeAction('stop'))
        j.tools.async.wrappers.sync(nbdserver.delete())

    j.tools.async.wrappers.sync(old_volume_container.executeAction('stop'))
    j.tools.async.wrappers.sync(old_volume_container.delete())



def monitor(job):
    pass
    # raise NotADirectoryError()

def processChange(job):
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        # mean we want to migrate vm from a node to another
        if 'node' in args and args['node'] != service.model.data.node:
            j.tools.async.wrappers.sync(service.executeAction('migrate', args={'node': args['node']}))
