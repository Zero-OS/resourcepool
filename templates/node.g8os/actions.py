from js9 import j


def init(job):
    from zeroos.orchestrator.sal.Node import Node
    service = job.service
    node = Node.from_ays(service)
    job.logger.info("create storage pool for fuse cache")
    poolname = "{}_fscache".format(service.name)

    storagepool = node.ensure_persistance(poolname)
    storagepool.ays.create(service.aysrepo)


def getAddresses(job):
    service = job.service
    networks = service.producers.get('network', [])
    networkmap = {}
    for network in networks:
        job = network.getJob('getAddresses', args={'node_name': service.name})
        networkmap[network.name] = j.tools.async.wrappers.sync(job.execute())
    return networkmap


def install(job):
    from zeroos.orchestrator.sal.Node import Node
    # at each boot recreate the complete state in the system
    service = job.service
    node = Node.from_ays(service)
    job.logger.info("mount storage pool for fuse cache")
    poolname = "{}_fscache".format(service.name)
    node.ensure_persistance(poolname)

    job.logger.info("configure networks")
    for network in service.producers.get('network', []):
        job = network.getJob('configure', args={'node_name': service.name})
        j.tools.async.wrappers.sync(job.execute())


def monitor(job):
    from zeroos.orchestrator.sal.Node import Node
    import redis
    service = job.service
    node = Node.from_ays(service)
    node.client.testConnectionAttempts = 0
    node.client.timeout = 15
    try:
        state = node.client.ping()
    except redis.ConnectionError:
        state = False

    if state:
        service.model.data.status = 'running'
    else:
        service.model.data.status = 'halted'
    service.saveAll()


def reboot(job):
    from zeroos.orchestrator.sal.Node import Node
    service = job.service
    job.logger.info("reboot node {}".format(service))
    node = Node.from_ays(service)
    node.client.raw('core.reboot', {})


def uninstall(job):
    service = job.service
    bootstraps = service.aysrepo.servicesFind(actor='bootstrap.g8os')
    if bootstraps:
        j.tools.async.wrappers.sync(bootstraps[0].getJob('delete_node', args={'node_name': service.name}).execute())
