from JumpScale import j


def input(job):
    # Check the blueprint input for errors
    args = job.model.args
    if args.get('volumes'):
        raise j.exceptions.Input('volumes property should not be set in the blueprint. Instead use disks property.')
    disks = args.get("disks", [])
    if disks:
        args['volumes'] = [disk['volumeid'] for disk in disks]
    return args


def get_node_client(service):
    node = service.parent
    return j.clients.g8core.get(host=node.model.data.redisAddr,
                                port=node.model.data.redisPort,
                                password=node.model.data.redisPassword)


def get_container_root(service, id):
    client = get_node_client(service)
    containers_info = client.container.list()
    id = str(id)
    if id in containers_info:
        return containers_info[id]['container']['root']

    raise j.exceptions.RuntimeError("container with id {} doesn't exists".format(id))


def create_nbdserver_container(service, parent):
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
            'flist': 'https://hub.gig.tech/gig-official-apps/gonbdserver-master.flist',
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
    volume_container = create_nbdserver_container(service, service.parent)

    for volume in service.producers.get('volume', []):
        job.logger.info("creates nbd server for vm {}".format(service.name))
        nbdserver = create_nbd(service, volume_container, volume)
        service.consume(nbdserver)


def install(job):
    service = job.service

    # get all path to the vdisks serve by the nbdservers
    medias = []
    for nbdserver in service.producers.get('nbdserver', []):
        # build full path of the nbdserver unix socket on the host filesystem
        container_root = get_container_root(service, nbdserver.parent.model.data.id)
        socket_path = j.sal.fs.joinPaths(container_root, nbdserver.model.data.socketPath.lstrip('/'))
        url = 'nbd+unix:///{id}?socket={socket}'.format(id=nbdserver.model.key, socket=socket_path)
        medias.append({'url': url})

        # make sure the container is started
        j.tools.async.wrappers.sync(nbdserver.parent.executeAction('start'))
        # make sure the nbdserver is started
        j.tools.async.wrappers.sync(nbdserver.executeAction('start'))

    job.logger.info("create vm {}".format(service.name))
    client = get_node_client(service)
    nics = []
    for nic in service.model.data.nics:
        nic = nic.to_dict()
        nic['hwaddr'] = nic.pop('macaddress', None)
        nics.append(nic)
    client.kvm.create(
        service.name,
        media=medias,
        cpu=service.model.data.cpu,
        memory=service.model.data.memory,
        nics=nics,
    )

    # TODO: test vm actually exists
    service.model.data.status = 'running'


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def stop(job):
    service = job.service

    job.logger.info("stop vm {}".format(service.name))
    client = get_node_client(service)
    for kvm in client.kvm.list():
        if kvm['name'] == service.name:
            client.kvm.destroy(kvm['uuid'])
            break

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
    volume_container = create_nbdserver_container(service, target_node)
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


def updatedevices(service, client, args):
    # mean we want to migrate vm from a node to another
    if 'node' in args and args['node'] != service.model.data.node:
        j.tools.async.wrappers.sync(service.executeAction('migrate', args={'node': args['node']}))
    if 'disks' in args['disks'] != service.model.data.disks:
            new_disks = set(args['disks']) - set(service.model.data.disks)
            if new_disks:
                new_disks = list(new_disks)
                for new_disk in new_disks:
                    client.experimental.kvm.attachDisk(service.name, new_disk)
            old_disks = set(service.model.data.disks) - set(args['disks'])
            if old_disks:
                old_disks = list(old_disks)
                for old_disk in old_disks:
                    client.experimental.kvm.detachDisk(service.name, old_disk)

# TODO removeNic and addNic not implmented as required code will be added when they are done.
    # if 'nics' in args['nics'] != service.model.data.nics:
    #     bp_nics = [(nic.id, nic.type) for nic in args['nics']]
    #     loaded_nics = [(nic.id, nic.type) for nic in service.model.data.nics]
    #     nics = set(bp_nics) - set(loaded_nics)
    #     if nics:
    #         nics = list(nics)
    #         for nic in nics:
    #             client.experimental.kvm.addNic(service.name, nic)
    #     nics = set(loaded_nics) - set(bp_nics)
    #     if nics:
    #         nics = list(nics)
    #         for nic in nics:
    #             client.experimental.kvm.removeNic(service.name, nic)


def monitor(job):
    pass
    # raise NotADirectoryError()


def processChange(job):
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        try:
            client = get_node_client(service)
            updatedevices(service, client, args)
        except ValueError:
            job.logger.error("vm {} doesn't exist, cant update devices", service.name)
