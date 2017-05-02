from JumpScale import j


def input(job):
    for arg in ['filesystems', 'arbds']:
        if job.model.args.get(arg, []) != []:
            raise j.exceptions.Input("{} should not be set as input".format(arg))


def get_cluster(service):
    from JumpScale.sal.g8os.StorageCluster import StorageCluster
    from JumpScale.sal.g8os.Node import Node

    nodes = []
    for node_service in service.producers['node']:
        nodes.append(Node.from_ays(node_service))

    return StorageCluster.from_ays(service)


def init(job):
    job.service.model.data.status = 'empty'


def install(job):
    from JumpScale.sal.g8os.Node import Node
    service = job.service

    job.service.model.data.status = 'deploying'

    nodes = []
    for node_service in service.producers['node']:
        nodes.append(Node.from_ays(node_service))

    job.logger.info("create cluster {}".format(service.name))
    cluster = j.sal.g8os.create_storagecluster(
        label=service.model.data.label,
        nodes=nodes,
        disk_type=str(service.model.data.diskType),
        nr_server=service.model.data.nrServer,
        has_slave=service.model.data.hasSlave,
    )
    job.logger.info("start cluster {}".format(service.name))
    cluster.start()
    service.model.data.status = 'ready'
    cluster.ays.create(service.aysrepo)


def start(job):
    service = job.service

    cluster = get_cluster(service)
    job.logger.info("start cluster {}".format(service.name))
    cluster.start()
    cluster.ays.create(service.aysrepo)
    job.service.model.data.status = 'ready'


def stop(job):
    service = job.service
    cluster = get_cluster(service)
    job.logger.info("stop cluster {}".format(service.name))
    cluster.stop()
    cluster.ays.create(service.aysrepo)


def delete(job):
    service = job.service
    cluster = get_cluster(service)
    job.logger.info("stop cluster {}".format(service.name))
    cluster.stop()
    job.service.model.data.status = 'empty'


def addStorageServer(job):
    raise NotImplementedError()


def reoveStorageServer(job):
    raise NotImplementedError()
