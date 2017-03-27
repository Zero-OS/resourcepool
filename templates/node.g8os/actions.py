
def install(job):
    # at each boot recreate the complete state in the system
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None,
    )
    # create storage pool for fuse cache
    storagepool = node.ensure_persistance()
    actor_storagepool = service.aysrepo.actorGet('storagepool')
    sp_args = {
        'status':'healthy',
        'totalCapacity':storagepool.size,
        'freeCapacity': storagepool.size - storagepool.used,
        # 'metadataProfile': storagepool.metadata_profile, #TODO: fix g8os sal to have btrfs profile in object
        # 'dataProfile': storagepool.data_profile,
        'mountpoint': storagepool.mountpoint,
        'devices': storagepool.devices,
        'node': service.name,
    }
    actor_storagepool.serviceCreate(instance='{}_{}'.format(service.name, storagepool.name), args=sp_args)

    # configure network
    # TODO


def reboot(job):
    raise NotImplementedError()
