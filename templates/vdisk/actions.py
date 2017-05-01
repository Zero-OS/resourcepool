from JumpScale import j


def install(job):
    import random
    from urllib.parse import urlparse
    service = job.service
    service.model.data.status = 'halted'
    if service.model.data.templateVdisk:
        services = service.aysrepo.servicesFind(role='grid_config')
        if len(services) <= 0:
            raise j.exceptions.NotFound("not grid_config service installed. {} can't get the grid API URL.".format(service))

        grid_addr = services[0].model.data.apiURL
        storagecluster = service.aysrepo.serviceGet(role='storage_cluster', instance=service.model.data.storageCluster)
        target_node = random.choice(storagecluster.producers['node'])

        volume_container = create_from_template_container(service, target_node)
        try:
            node_client = j.clients.g8core.get(host=target_node.model.data.redisAddr,
                                               port=target_node.model.data.redisPort,
                                               password=target_node.model.data.redisPassword)
            config = node_client.config.get()
            masterardb = urlparse(config['globals']['storage']).netloc
            CMD = '/bin/copyvdisk -sourcetype direct -targettype api {src_name} {dst_name} {masterardb} {grid_addr}'
            cmd = CMD.format(dst_name=service.name, src_name=service.model.data.templateVdisk, grid_addr=grid_addr,
                             masterardb=masterardb)
            print(cmd)
            result = volume_container.client.system(cmd).get()
            if result.state != 'SUCCESS':
                raise j.exceptions.RuntimeError("Failed to copyvdisk {} {}".format(result.stdout, result.stderr))

        finally:
            destroy_from_template_container(service, target_node)


def create_from_template_container(service, parent):
    """
    if not it creates it.
    return the container service
    """
    from JumpScale.sal.g8os.Container import Container
    from JumpScale.sal.g8os.Node import Node
    container_name = 'vdisk_{}_{}'.format(service.name, parent.name)
    try:
        container = service.aysrepo.serviceGet(role='container', instance=container_name)
    except j.exceptions.NotFound:
        container = None
    if container:
        container.delete()

    node = Node.from_ays(parent)
    container = Container(name=container_name,
                          flist='https://hub.gig.tech/gig-official-apps/blockstor-master.flist',
                          host_network=True,
                          node=node)
    containerservice = container.ays.create(service.aysrepo)
    j.tools.async.wrappers.sync(containerservice.executeAction('install'))
    return container


def destroy_from_template_container(service, parent):
    """
    first check if the volumes container for this vm exists.
    if not it creates it.
    return the container service
    """
    container_name = 'vdisk_{}_{}'.format(service.name, parent.name)
    try:
        container = service.aysrepo.serviceGet(role='container', instance=container_name)
    except j.exceptions.NotFound:
        container = None
    else:
        j.tools.async.wrappers.sync(container.executeAction('stop'))
        j.tools.async.wrappers.sync(container.delete())


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
