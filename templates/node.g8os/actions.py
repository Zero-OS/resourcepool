from JumpScale import j


def install(job):
    import asyncio

    # at each boot recreate the complete state in the system
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )

    job.logger.info("create storage pool for fuse cache")
    poolname = "{}_fsache".format(service.name)
    storagepool = node.ensure_persistance(poolname)
    actor_storagepool = service.aysrepo.actorGet('storagepool')
    sp_args = {
        'status': 'healthy',
        'totalCapacity': storagepool.size,
        'freeCapacity': storagepool.size - storagepool.used,
        'metadataProfile': storagepool.fsinfo['metadata']['profile'],
        'dataProfile': storagepool.fsinfo['data']['profile'],
        'mountpoint': storagepool.mountpoint,
        'devices': storagepool.devices,
        'node': service.name,
    }
    actor_storagepool.serviceCreate(instance=poolname, args=sp_args)

    job.logger.info("configure networks")
    loop = asyncio.get_event_loop()
    futures = []
    for network in service.producers.get('network', []):
        job = network.getJob('configure', args={'node_name': service.name})
        futures.append(job.execute())

    if futures:
        loop.run_until_complete(asyncio.gather(*futures))


def reboot(job):
    service = job.service
    job.logger.info("reboot node {}".format(service))
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )
    node.client.raw('core.reboot', {})
