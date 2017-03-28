from JumpScale import j


def install(job):
    # at each boot recreate the complete state in the system
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )
    # create storage pool for fuse cache
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

    # configure network
    # TODO


def reboot(job):
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )
    node.client.raw('core.reboot', {})
