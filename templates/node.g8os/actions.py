from JumpScale import j


def init(job):
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )

    job.logger.info("create storage pool for fuse cache")
    poolname = "{}_fscache".format(service.name)

    storagepool = node.ensure_persistance(poolname)
    storagepool.ays.create(service.aysrepo)


def getAddresses(job):
    import asyncio
    service = job.service
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    futures = []
    networks = service.producers.get('network', [])
    for network in networks:
        job = network.getJob('getAddresses', args={'node_name': service.name})
        futures.append(job.execute())

    if futures:
        return {i.name: j for i, j in zip(networks, loop.run_until_complete(asyncio.gather(*futures)))}
    else:
        return {}


def install(job):
    import asyncio

    # at each boot recreate the complete state in the system
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )

    job.logger.info("mount storage pool for fuse cache")
    poolname = "{}_fscache".format(service.name)
    node.ensure_persistance(poolname)

    job.logger.info("configure networks")
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    futures = []
    for network in service.producers.get('network', []):
        job = network.getJob('configure', args={'node_name': service.name})
        futures.append(job.execute())

    if futures:
        loop.run_until_complete(asyncio.gather(*futures))


def monitor(job):
    import redis
    service = job.service
    addr = service.model.data.redisAddr
    node = j.clients.g8core.get(addr, testConnectionAttempts=0)
    node.timeout = 15
    try:
        state = node.ping()
    except redis.ConnectionError as e:
        state = False

    if state:
        service.model.data.status = 'running'
    else:
        service.model.data.status = 'halted'
    service.saveAll()


def reboot(job):
    service = job.service
    job.logger.info("reboot node {}".format(service))
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )
    node.client.raw('core.reboot', {})


def uninstall(job):
    service = job.service
    bootstraps = service.aysrepo.servicesFind(actor='bootstrap.g8os')
    if bootstraps:
        j.tools.async.wrappers.sync(bootstraps[0].getJob('delete_node', args={'node_name': service.name}).execute())
