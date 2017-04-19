from JumpScale import j


def install(job):
    service = job.service
    service.model.data.status = 'halted'
    if service.model.data.templateVolume:
        services = service.aysrepo.servicesFind(role='grid_config')
        if len(services) <= 0:
            raise j.exceptions.NotFound("not grid_config service installed. {} can't get the grid API URL.".format(service))

        grid_addr = services[0].model.data.apiURL

        args = job.model.args
        target_node = service.aysrepo.serviceGet('node', args['node'])

        volume_container = create_nbdserver_container(service, target_node)
        try:
            node_client = j.clients.g8core.get(host=target_node.model.data.redisAddr,
                                               port=target_node.model.data.redisPort,
                                               password=target_node.model.data.redisPassword)
            container_client = node_client.container.client(volume_container.model.data.id)
            CMD = 'copyvolume -t api {src_name} {dst_name} -a {grid_addr} {src_storagecluster} {dst_storagecluster}'
            cmd = CMD.format(src_name=service.name, dst_name=service.model.data.templateVolume.name, grid_addr=grid_addr,
                             src_storagecluster=service.model.data.storageCluster.name, dst_storagecluster=service.model.data.templateVolume.name)
            container_client.bash(cmd)

        finally:
            destroy_nbdserver_container(service, target_node)


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
            'flist': 'https://hub.gig.tech/gig-official-apps/blockstor-master.flist',
            'hostNetworking': True,
        }
        container = container_actor.serviceCreate(instance=container_name, args=args)

    return container


def destroy_nbdserver_container(service, parent):
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
    else:
        container.delete()

def start(job):
    service = job.service
    service.model.data.status = 'running'


def pause(job):
    service = job.service
    service.model.data.status = 'halted'


def rollback(job):
    service = job.service
    service.model.data.status = 'rollingback'
    # TODO: rollback disk
    service.model.data.status = 'running'


def resize(job):
    service = job.service
    job.logger.info("resize vdisk {}".format(service.name))

    if 'size' not in job.model.args:
        raise j.exceptions.Input("size is not present in the arguments of the job")

    size = int(job.model.args['size'])
    if size < service.model.data.size:
        raise j.exceptions.Input("size is smaller then current size, disks can grown")

    service.model.data.size = size


def processChange(job):
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        j.tools.async.wrappers.sync(service.executeAction('resize', args={'size': args['size']}))
