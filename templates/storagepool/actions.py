from JumpScaler import j


def input(job):
    service = job.service
    for notempty in ['mountpoint', 'metadataProfile', 'dataProfile', 'devices']:
        if job.model.args.get(notempty, "") == "":
            raise j.exceptions.Input("{} argument cannot be empty, cannot continue init of {}".format(notempty, service))


def install(job):
    service = job.service
    pservice = service.parent
    node = j.sal.g8os.get_node(
        addr=pservice.model.data.redisAddr,
        port=pservice.model.data.redisPort,
        password=pservice.model.data.redisPassword or None,
    )
    devices = list(service.model.data.devices)
    name = service.name
    dataProfile = str(service.model.data.dataProfile)
    metadataProfile = str(service.model.data.metadataProfile)
    mountpoint = str(service.model.data.mountpoint)
    try:
        pool = node.storagepools.get(name)
    except ValueError:
        # pool does not exists lets create it
        pool = node.storagepools.create(name, devices, metadataProfile, dataProfile)

    # mount device
    if pool.mountpoint:
        if pool.mountpoint != mountpoint:
            pool.umount(mountpoint)
            pool.mount(mountpoint)
    else:
        pool.mount(mountpoint)

    # lets check if devices need to be added removed and the profile still matches
    if pool.fsinfo['data']['profile'].lower() != dataProfile:
        raise RuntimeError("Data profile of storagepool {} does not match".format(name))
    if pool.fsinfo['metadata']['profile'].lower() != metadataProfile:
        raise RuntimeError("Metadata profile of storagepool {} does not match".format(name))

    pooldevices = set(pool.devices)
    requireddevices = set(devices)

    # add extra devices
    extradevices = requireddevices - pooldevices
    pool.device_add(*extradevices)

    # remove devices
    removeddevices = pooldevices - requireddevices
    pool.device_remove(*removeddevices)


def delete(job):
    service = job.service
    pservice = service.parent
    node = j.sal.g8os.get_node(
        addr=pservice.model.data.redisAddr,
        port=pservice.model.data.redisPort,
        password=pservice.model.data.redisPassword or None,
    )
    name = service.name
    node.storagepools.destroy(name)
