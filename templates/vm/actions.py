from JumpScale import j


def input(job):
    # Check the blueprint input for errors
    args = job.model.args
    if args.get('vdisks'):
        raise j.exceptions.Input('vdisks property should not be set in the blueprint. Instead use disks property.')
    disks = args.get("disks", [])
    if disks:
        args['vdisks'] = [disk['vdiskid'] for disk in disks]
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
    first check if the vdisks container for this vm exists.
    if not it creates it.
    return the container service
    """
    container_name = 'vdisks_{}_{}'.format(service.name, parent.name)
    try:
        container = service.aysrepo.serviceGet(role='container', instance=container_name)
    except j.exceptions.NotFound:
        container = None

    if container is None:
        container_actor = service.aysrepo.actorGet('container')
        args = {
            'node': parent.name,
            'flist': 'https://hub.gig.tech/gig-official-apps/blockstor-master.flist',
            'hostNetworking': True
        }
        container = container_actor.serviceCreate(instance=container_name, args=args)

    # make sure the container has the right parent, the node where this vm runs.
    container.model.changeParent(service.parent)

    return container


def create_nbd(service, container, vdisk):
    """
    first check if the nbd server for a specific vdisk exists.
    if not it creates it.
    return the nbdserver service
    """
    nbd_name = vdisk.name

    try:
        nbdserver = service.aysrepo.serviceGet(role='container', instance=nbd_name)
    except j.exceptions.NotFound:
        nbdserver = None

    if nbdserver is None:
        nbd_actor = service.aysrepo.actorGet('nbdserver')
        args = {
            # 'backendControllerUrl': '', #FIXME
            # 'vdiskControllerUrl': '', #FIXME
            'container': container.name,
        }
        nbdserver = nbd_actor.serviceCreate(instance=nbd_name, args=args)

    return nbdserver


def init(job):
    service = job.service

    # creates all nbd servers for each vdisk this vm uses
    job.logger.info("creates vdisks container for vm {}".format(service.name))
    vdisk_container = create_nbdserver_container(service, service.parent)

    for vdisk in service.producers.get('vdisk', []):
        job.logger.info("creates nbd server for vm {}".format(service.name))
        nbdserver = create_nbd(service, vdisk_container, vdisk)
        service.consume(nbdserver)


def install(job):
    import time
    service = job.service

    # get all path to the vdisks serve by the nbdservers
    medias = []
    for nbdserver in service.producers.get('nbdserver', []):
        # build full path of the nbdserver unix socket on the host filesystem
        container = nbdserver.parent
        if container.model.data.id == 0:
            # start container
            j.tools.async.wrappers.sync(container.executeAction('start'))
        container_root = get_container_root(service, container.model.data.id)
        socket_path = j.sal.fs.joinPaths(container_root, nbdserver.model.data.socketPath.lstrip('/'))
        url = 'nbd+unix:///{id}?socket={socket}'.format(id=nbdserver.model.name, socket=socket_path)
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

    kvm = get_domain(service)
    if not kvm:
        client.kvm.create(
            service.name,
            media=medias,
            cpu=service.model.data.cpu,
            memory=service.model.data.memory,
            nics=nics,
        )
        # wait for max 60 seconds for vm to be running
        start = time.time()
        while start + 60 > time.time():
            if get_domain(service):
                break
            else:
                time.sleep(3)
        else:
            raise j.exceptions.RuntimeError("Failed to start vm {}".format(service.name))

    service.model.data.status = 'running'


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def get_domain(service):
    client = get_node_client(service)
    for kvm in client.kvm.list():
        if kvm['name'] == service.name:
            return kvm
            break


def stop(job):
    service = job.service
    job.logger.info("stop vm {}".format(service.name))
    client = get_node_client(service)
    kvm = get_domain(service)
    if kvm:
        client.kvm.destroy(kvm['uuid'])

    for nbdserver in service.producers.get('nbdserver', []):
        job.logger.info("stop nbdserver for vm {}".format(service.name))
        # make sure the nbdserver is stopped
        j.tools.async.wrappers.sync(nbdserver.executeAction('stop'))

    job.logger.info("stop vdisks container for vm {}".format(service.name))
    try:
        container_name = 'vdisks_{}_{}'.format(service.name, service.parent.name)
        container = service.aysrepo.serviceGet(role='container', instance=container_name)
        j.tools.async.wrappers.sync(container.executeAction('stop'))
    except j.exceptions.NotFound:
        job.logger.info("container doesn't exists.")

    service.model.data.status = 'halted'


def pause(job):
    service = job.service
    job.logger.info("pause vm {}".format(service.name))
    client = get_node_client(service)
    kvm = get_domain(service)
    if kvm:
        client.kvm.pause(kvm['uuid'])
        service.model.data.status = 'paused'


def resume(job):
    service = job.service
    job.logger.info("resume vm {}".format(service.name))
    client = get_node_client(service)
    kvm = get_domain(service)
    if kvm:
        client.kvm.resume(kvm['uuid'])
        service.model.data.status = 'running'


def shutdown(job):
    import time
    service = job.service
    job.logger.info("shutdown vm {}".format(service.name))
    client = get_node_client(service)
    kvm = get_domain(service)
    if kvm:
        client.kvm.shutdown(kvm['uuid'])
        service.model.data.status = 'halting'
        # wait for max 60 seconds for vm to be shutdown
        start = time.time()
        while start + 60 > time.time():
            kvm = get_domain(service)
            if kvm and kvm['state'] == 'shutdown':
                service.model.data.status = 'halted'
                break
            else:
                time.sleep(3)
        else:
            raise j.exceptions.RuntimeError("Failed to shutdown vm {}".format(service.name))


def migrate(job):
    service = job.service

    service.model.data.status = 'migrating'

    args = job.model.args
    if 'node' not in args:
        raise j.exceptions.Input("migrate action expect to have the destination node in the argument")

    target_node = service.aysrepo.serviceGet('node', args['node'])
    job.logger.info("start migration of vm {} from {} to {}".format(service.name, service.parent.name, target_node.name))

    old_nbd = service.producers.get('nbdserver', [])
    container_name = 'vdisks_{}_{}'.format(service.name, service.parent.name)
    old_vdisk_container = service.aysrepo.serviceGet('container', container_name)

    # start new nbdserver on target node
    vdisk_container = create_nbdserver_container(service, target_node)
    for vdisk in service.producers.get('vdisk', []):
        job.logger.info("start nbd server for migration of vm {}".format(service.name))
        nbdserver = create_nbd(service, vdisk_container, vdisk)
        service.consume(nbdserver)
        vdisk.model.data.node = target_node.name

    # TODO: migrate domain, not impleented yet in core0

    service.model.changeParent(target_node)
    service.model.data.status = 'running'

    # delete current nbd services and volue container
    job.logger.info("delete current nbd services and vdisk container")
    for nbdserver in old_nbd:
        j.tools.async.wrappers.sync(nbdserver.executeAction('stop'))
        j.tools.async.wrappers.sync(nbdserver.delete())

    j.tools.async.wrappers.sync(old_vdisk_container.executeAction('stop'))
    j.tools.async.wrappers.sync(old_vdisk_container.delete())


def updatedevices(service, client, args):
    # mean we want to migrate vm from a node to another
    if 'node' in args and args['node'] != service.model.data.node:
        j.tools.async.wrappers.sync(service.executeAction('migrate', args={'node': args['node']}))
    if 'disks' in args['disks'] != service.model.data.disks:
            new_disks = set(args['disks']) - set(service.model.data.disks)
            if new_disks:
                new_disks = list(new_disks)
                for new_disk in new_disks:
                    client.kvm.attachDisk(service.name, new_disk)
            old_disks = set(service.model.data.disks) - set(args['disks'])
            if old_disks:
                old_disks = list(old_disks)
                for old_disk in old_disks:
                    client.kvm.detachDisk(service.name, old_disk)

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


def update_data(job, client, args):
    service = job.service

    service.model.data.memory = args['memory']
    service.model.data.cpu = args['cpu']
    stop(job)
    start(job)


def processChange(job):
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        try:
            client = get_node_client(service)
            update_data(job, client, args)
            updatedevices(service, client, args)
        except ValueError:
            job.logger.error("vm {} doesn't exist, cant update devices", service.name)
