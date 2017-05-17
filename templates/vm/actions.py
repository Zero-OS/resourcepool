from JumpScale import j


def input(job):
    # Check the blueprint input for errors
    args = job.model.args
    if args.get('vdisks'):
        raise j.exceptions.Input('vdisks property should not be set in the blueprint. Instead use disks property.')
    disks = args.get("disks", [])
    if disks != []:
        args['vdisks'] = [disk['vdiskid'] for disk in disks]
    return args


def get_node(service):
    from JumpScale.sal.g8os.Node import Node
    return Node.from_ays(service.parent)


def create_nbdserver_container(service, parent):
    """
    first check if the vdisks container for this vm exists.
    if not it creates it.
    return the container service
    """
    actor = service.aysrepo.actorGet("container")
    args = {
        'node': parent.name,
        'flist': 'https://hub.gig.tech/gig-official-apps/blockstor-master.flist',
        'hostNetworking': True,
    }
    container_name = 'vdisks_{}_{}'.format(service.name, parent.name)
    containerservice = actor.serviceCreate(instance=container_name, args=args)
    # make sure the container has the right parent, the node where this vm runs.
    containerservice.model.changeParent(service.parent)
    j.tools.async.wrappers.sync(containerservice.executeAction('start'))

    return containerservice


def create_nbd(service, container, vdisk):
    """
    first check if the nbd server for a specific vdisk exists.
    if not it creates it.
    return the nbdserver service
    """
    nbd_name = vdisk.name

    try:
        nbdserver = service.aysrepo.serviceGet(role='nbdserver', instance=nbd_name)
    except j.exceptions.NotFound:
        nbdserver = None

    if nbdserver is None:
        nbd_actor = service.aysrepo.actorGet('nbdserver')
        args = {
            # 'backendControllerUrl': '', # FIXME
            # 'vdiskControllerUrl': '', # FIXME
            'container': container.name,
        }
        nbdserver = nbd_actor.serviceCreate(instance=nbd_name, args=args)

    return nbdserver


def _init_nbd_services(job, vdisk_container, vdisks):
    service = job.service
    for vdisk in vdisks:
        if isinstance(vdisk, str):
            try:
                vdisk = service.aysrepo.serviceGet(role='vdisk', instance=vdisk)
            except j.exceptions.NotFound:
                raise j.exceptions.RuntimeError("Service vdisk!{} not found".format(vdisk))

        job.logger.info("creates nbd server for vm {}".format(service.name))
        nbdserver = create_nbd(service, vdisk_container, vdisk)
        service.consume(nbdserver)


def _nbd_url(container, nbdserver):
    container_root = container.info['container']['root']
    socket_path = j.sal.fs.joinPaths(container_root, nbdserver.model.data.socketPath.lstrip('/'))
    return 'nbd+unix:///{id}?socket={socket}'.format(id=nbdserver.model.name, socket=socket_path)


def init(job):
    service = job.service

    # creates all nbd servers for each vdisk this vm uses
    job.logger.info("creates vdisks container for vm {}".format(service.name))
    vdisk_container = create_nbdserver_container(service, service.parent)
    _init_nbd_services(job, vdisk_container, service.producers.get('vdisk', []))


def _start_nbds(service):
    from JumpScale.sal.g8os.Container import Container

    # get all path to the vdisks serve by the nbdservers
    medias = []
    for nbdserver in service.producers.get('nbdserver', []):
        # build full path of the nbdserver unix socket on the host filesystem
        container = Container.from_ays(nbdserver.parent)
        if not container.is_running():
            # start container
            j.tools.async.wrappers.sync(nbdserver.parent.executeAction('start'))

        # make sure the nbdserver is started
        j.tools.async.wrappers.sync(nbdserver.executeAction('start'))
        url = _nbd_url(container, nbdserver)
        medias.append({'url': url})
    return medias


def get_media_for_disk(medias, disk):
    from urllib.parse import urlparse
    for media in medias:
        url = urlparse(media['url'])
        if disk['vdiskid'] == url.path.lstrip('/'):
            return media


def install(job):
    import time
    service = job.service

    # get all path to the vdisks serve by the nbdservers
    medias = _start_nbds(service)

    job.logger.info("create vm {}".format(service.name))
    node = get_node(service)
    nics = []
    for nic in service.model.data.nics:
        nic = nic.to_dict()
        nic['hwaddr'] = nic.pop('macaddress', None)
        nics.append(nic)
    for disk in service.model.data.disks:
        if disk.maxIOps > 0:
            media = get_media_for_disk(medias, disk.to_dict())
            media['iotune'] = {'totaliopssec': disk.maxIOps,
                               'totaliopssecset': True}

    kvm = get_domain(service)
    if not kvm:
        node.client.kvm.create(
            service.name,
            media=medias,
            cpu=service.model.data.cpu,
            memory=service.model.data.memory,
            nics=nics,
        )
        # wait for max 60 seconds for vm to be running
        start = time.time()
        while start + 60 > time.time():
            kvm = get_domain(service)
            if kvm:
                service.model.data.vnc = kvm['vnc']
                break
            else:
                time.sleep(3)
        else:
            service.model.data.status = 'error'
            raise j.exceptions.RuntimeError("Failed to start vm {}".format(service.name))

    service.model.data.status = 'running'
    service.saveAll()


def start(job):
    service = job.service
    service.model.data.status = 'starting'
    service.saveAll()
    j.tools.async.wrappers.sync(service.executeAction('install'))


def get_domain(service):
    node = get_node(service)
    for kvm in node.client.kvm.list():
        if kvm['name'] == service.name:
            return kvm


def stop(job):
    service = job.service
    job.logger.info("stop vm {}".format(service.name))
    node = get_node(service)
    kvm = get_domain(service)
    if kvm:
        node.client.kvm.destroy(kvm['uuid'])

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
    service.model.data.vnc = -1
    service.saveAll()


def pause(job):
    service = job.service
    job.logger.info("pause vm {}".format(service.name))
    node = get_node(service)
    kvm = get_domain(service)
    if kvm:
        node.client.kvm.pause(kvm['uuid'])
        service.model.data.status = 'paused'
        service.saveAll()


def resume(job):
    service = job.service
    job.logger.info("resume vm {}".format(service.name))
    node = get_node(service)
    kvm = get_domain(service)
    if kvm:
        node.client.kvm.resume(kvm['uuid'])
        service.model.data.status = 'running'
        service.saveAll()


def shutdown(job):
    import time
    service = job.service
    job.logger.info("shutdown vm {}".format(service.name))
    node = get_node(service)
    kvm = get_domain(service)
    if kvm:
        service.model.data.status = 'halting'
        node.client.kvm.shutdown(kvm['uuid'])
        # wait for max 60 seconds for vm to be shutdown
        start = time.time()
        while start + 60 > time.time():
            kvm = get_domain(service)
            if kvm:
                time.sleep(3)
            else:
                service.model.data.status = 'halted'
                break
        else:
            service.model.data.status = 'error'
            raise j.exceptions.RuntimeError("Failed to shutdown vm {}".format(service.name))
    else:
        service.model.data.status = 'halted'

    
    service.saveAll()


def migrate(job):
    service = job.service

    service.model.data.status = 'migrating'
    
    node = job.service.model.data.node
    if not node:
        raise j.exceptions.Input("migrate action expect to have the destination node in the argument")

    target_node = service.aysrepo.serviceGet('node', node)
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
    service.saveAll()


def _remove_duplicates(col):
    try:
        return [dict(t) for t in set([tuple(element.items()) for element in col])]
    except AttributeError:
        return [dict(t) for t in set([tuple(element.to_dict().items()) for element in col])]


def _diff(col1, col2):
    col1 = _remove_duplicates(col1)
    col2 = _remove_duplicates(col2)
    return [elem for elem in col1 if elem not in col2]


def updateDisks(job, client, args):
    from JumpScale.sal.g8os.Container import Container
    service = job.service

    vdisk_container = create_nbdserver_container(service, service.parent)
    uuid = get_domain(service)['uuid']

    # mean we want to migrate vm from a node to another
    if 'node' in args and args['node'] != service.model.data.node:
        j.tools.async.wrappers.sync(service.executeAction('migrate', args={'node': args['node']}))

    # Get new and old disks
    new_disks = _diff(args['disks'], service.model.data.disks)
    old_disks = _diff(service.model.data.disks, args['disks'])

    # Do nothing if no disk change
    if new_disks == [] and old_disks == []:
        return

    old_disks_id = [disk['vdiskid'] for disk in old_disks]

    # Set model to new data
    service.model.data.disks = args['disks']
    service.model.data.vdisks = [disk['vdiskid'] for disk in args['disks']]

    # Detatching and Cleaning old disks
    if old_disks != []:
        for nbdserver in service.producers.get('nbdserver', []):
            nbdserver_name = nbdserver.name
            if nbdserver_name in old_disks_id:
                container = Container.from_ays(nbdserver.parent)
                url = _nbd_url(container, nbdserver)
                client.client.kvm.detach_disk(uuid, {'url': url})
                j.tools.async.wrappers.sync(nbdserver.executeAction('stop'))
                j.tools.async.wrappers.sync(nbdserver.delete())

    # Attaching new disks
    if new_disks != []:
        _init_nbd_services(job, vdisk_container, service.model.data.vdisks)
        medias = _start_nbds(service)
        for disk in new_disks:
            media = get_media_for_disk(medias, disk)
            if disk['maxIOps']:
                media['iotune'] = {'totaliopssec': disk['maxIOps'],
                                   'totaliopssecset': True}
            client.client.kvm.attach_disk(uuid, media)
    service.saveAll()


def updateNics(job, client, args):
    service = job.service
    uuid = get_domain(service)['uuid']

    # Get new and old disks
    new_nics = _diff(args['nics'], service.model.data.nics)
    old_nics = _diff(service.model.data.nics, args['nics'])
    # Do nothing if no nic change
    if new_nics == [] and old_nics == []:
        return

    # Add new nics
    for nic in new_nics:
        if nic not in service.model.data.nics:
            client.client.kvm.add_nic(uuid=uuid,
                                      type=nic['type'],
                                      id=nic['id'] or None,
                                      hwaddr=nic['macaddress'] or None)

    # Remove old nics
    for nic in old_nics:
        client.client.kvm.remove_nic(uuid=uuid,
                                     type=nic['type'],
                                     id=nic['id'] or None,
                                     hwaddr=nic['macaddress'] or None)

    service.model.data.nics = args['nics']
    service.saveAll()


def monitor(job):
    pass
    # raise NotADirectoryError()


def update_data(job, args):
    service = job.service
    service.model.data.node = args.get('node', service.model.data.node)
    service.model.data.memory = args.get('memory', service.model.data.memory)
    service.model.data.cpu = args.get('cpu', service.model.data.cpu)


def processChange(job):
    service = job.service
    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        try:
            node = get_node(service)
            update_data(job, args)
            updateDisks(job, node, args)
            updateNics(job, node, args)
        except ValueError:
            job.logger.error("vm {} doesn't exist, cant update devices", service.name)
