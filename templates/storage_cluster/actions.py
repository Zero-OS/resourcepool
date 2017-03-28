from JumpScale import j


def init(job):
    service = job.service
    service.model.data.status = 'deploying'
    service.save()

    storagepool_actor = service.aysrepo.actorGet('storagepool')
    filesystem_actor = service.aysrepo.actorGet('filesystem')
    container_actor = service.aysrepo.actorGet('container')
    ardb_actor = service.aysrepo.actorGet('ardb')

    filesystems = []

    # create storagepool and filesystem services
    for node_service in service.producers['node']:
        node = j.sal.g8os.get_node(
            addr=node_service.model.data.redisAddr,
            port=node_service.model.data.redisPort,
            password=node_service.model.data.redisPassword or None,
        )

        available_disks = node.disks.list()
        usedisks = []
        for pool in (node.client.btrfs.list() or []):
            for device in pool['devices']:
                usedisks.append(device['path'])

        for disk in available_disks[::-1]:
            if disk.devicename in usedisks:
                available_disks.remove(disk)
                continue
            if disk.type.name != str(service.model.data.diskType):
                available_disks.remove(disk)
                continue

        for disk in available_disks:
            name = "{}_{}".format(node_service.name, disk.name)
            sp_args = {
                'status': 'healthy',
                'totalCapacity': disk.size,
                # 'freeCapacity': storagepool.size - storagepool.used,
                'metadataProfile': 'single',
                'dataProfile': 'single',
                # 'mountpoint': "/storage/{}".format(disk.name),
                'devices': [disk.devicename],
                'node': node_service.name,
            }
            sp_service = storagepool_actor.serviceCreate(instance=name, args=sp_args)

            fs_args = {
                'storagePool': sp_service.name,
                'readOnly': False,
                'quota': 0,
                'mountpoint': "/storage/{}".format(disk.name),
            }
            fs_service = filesystem_actor.serviceCreate(instance=name, args=fs_args)
            filesystems.append(fs_service)

    # distribute data ardb server on all the filesystems available
    ardb_services = []
    for i in range(service.model.data.nbrServer):
        fs_service = filesystems[i % len(filesystems) - 1]

        container_args = {
            'node': fs_service.parent.parent.name,
            'hostNetworking': True,
        }
        container_service = container_actor.serviceCreate(
            instance="{}_data{}".format(service.name, i),
            args=container_args
        )

        ardb_args = {
            'homeDir': fs_service.model.data.mountpoint,
            'bind': '0.0.0.0',  # FIXME: should be 40G network
            'container': container_service.name,
        }
        ardb_service = ardb_actor.serviceCreate(
            instance="{}_data{}".format(service.name, i),
            args=ardb_args
        )
        service.consume(ardb_service)
        ardb_services.append(ardb_service)

    # create metadata ardb
    fs_service = filesystems[(service.model.data.nbrServer + 1) % len(filesystems) - 1]

    container_args = {
        'node': fs_service.parent.parent.name,
        'hostNetworking': True,
    }
    container_service = container_actor.serviceCreate(
        instance="{}_metadata0".format(service.name),
        args=container_args
    )

    ardb_args = {
        'homeDir': fs_service.model.data.mountpoint,
        'bind': '0.0.0.0:16379',  # FIXME: should be 40G network
        'container': container_service.name,
    }
    ardb_service = ardb_actor.serviceCreate(
        instance="{}_metadata0".format(service.name),
        args=ardb_args
    )
    service.consume(ardb_service)
    ardb_services.append(ardb_service)

    if service.model.data.hasSlave:
        # deploy a slave for each ardb

        for ardb_service in ardb_services:
            # slave must be on a different node as the master
            master_node = ardb_service.parent.parent
            slave_fs = None
            for fs in filesystems:
                if fs.parent.parent.name != master_node.name:
                    slave_fs = fs

            if slave_fs is None:
                raise j.exceptions.RuntimeError("can't find a node to deploy slave of {}".format(ardb_service))

            container_args = {
                'node': slave_fs.parent.parent.name,
                'hostNetworking': True,
            }
            container_service = container_actor.serviceCreate(
                instance=ardb_service.parent.name + '_slave',
                args=container_args
            )

            ardb_args = {
                'homeDir': slave_fs.model.data.mountpoint,
                'bind': '0.0.0.0:16379',  # FIXME: should be 40G network
                'container': container_service.name,
            }
            ardb_service = ardb_actor.serviceCreate(
                instance=ardb_service.name + '_slave',
                args=ardb_args
            )
            service.consume(ardb_service)


def install(job):
    # since we consume all the ardb, this will be called once everything is ready
    job.service.model.data.status = 'ready'


def delete(job):
    # since we consume all the ardb, this will be called once everything is deleted
    job.service.model.data.status = 'empty'


def addStorageServer(job):
    raise NotImplementedError()


def reoveStorageServer(job):
    raise NotImplementedError()
