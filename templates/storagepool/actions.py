from JumpScaler import j


def input(job):
    service = job.service
    for notempty in ['metadataProfile', 'dataProfile', 'devices']:
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

    devices = [d.device for d in service.model.data.devices]
    name = service.name
    dataProfile = str(service.model.data.dataProfile)
    metadataProfile = str(service.model.data.metadataProfile)
    mountpoint = str(service.model.data.mountpoint) or None
    try:
        pool = node.storagepools.get(name)
    except ValueError:
        # pool does not exists lets create it
        pool = node.storagepools.create(name, devices, metadataProfile, dataProfile, overwrite=True)

    # mount device
    if mountpoint:
        if pool.mountpoint:
            if pool.mountpoint != mountpoint:
                pool.umount()
                pool.mount(mountpoint)
        else:
            pool.mount(mountpoint)

    # lets check if devices need to be added removed and the profile still matches
    if pool.fsinfo['data']['profile'].lower() != dataProfile:
        raise RuntimeError("Data profile of storagepool {} does not match".format(name))
    if pool.fsinfo['metadata']['profile'].lower() != metadataProfile:
        raise RuntimeError("Metadata profile of storagepool {} does not match".format(name))

    updateDevices(service, pool, devices)

    # update the mapping between uuid and device name
    pool.ays.create(service.aysrepo)


def delete(job):
    service = job.service
    pservice = service.parent
    node = j.sal.g8os.get_node(
        addr=pservice.model.data.redisAddr,
        port=pservice.model.data.redisPort,
        password=pservice.model.data.redisPassword or None,
    )
    name = service.name

    try:
        pool = node.storagepools.get(name)
        pool.delete()
    except ValueError:
        # pool does not exists, nothing to do
        pass


def updateDevices(service, pool, devices):
    pooldevices = set(pool.devices)
    requireddevices = set(devices)

    # add extra devices
    extradevices = requireddevices - pooldevices
    if extradevices:
        pool.device_add(*extradevices)

    # remove devices
    removeddevices = pooldevices - requireddevices
    if removeddevices:
        pool.device_remove(*removeddevices)

    pool.ays.create(service.aysrepo)


def processChange(job):
    service = job.service
    pservice = service.parent
    node = j.sal.g8os.get_node(
        addr=pservice.model.data.redisAddr,
        port=pservice.model.data.redisPort,
        password=pservice.model.data.redisPassword or None,
    )

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema":
        try:
            pool = node.storagepools.get(service.name)
            devices = [d['device'] for d in args['devices']]
            updateDevices(service, pool, devices)
        except ValueError:
            job.logger.error("pool {} doesn't exist, cant update devices", service.name)
