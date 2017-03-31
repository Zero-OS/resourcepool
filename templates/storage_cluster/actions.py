from JumpScale import j

def input(job):
    for arg in ['filesystems', 'arbds']:
        if job.model.args.get(arg, []) != []:
            raise j.exceptions.Input("{} should not be set as input".format(arg))

def create_filesystem(storagecluster_service, node_service, instance, disk):
    storagepool_actor = storagecluster_service.aysrepo.actorGet('storagepool')
    filesystem_actor = storagecluster_service.aysrepo.actorGet('filesystem')

    sp_args = {
        'status': 'healthy',
        'totalCapacity': disk.size,
        'metadataProfile': 'single',
        'dataProfile': 'single',
        'mountpoint': "/storage/{}".format(disk.name),
        'devices': [disk.devicename],
        'node': node_service.name,
    }
    sp_service = storagepool_actor.serviceCreate(instance=instance, args=sp_args)

    fs_args = {
        'storagePool': sp_service.name,
        'readOnly': False,
        'quota': 0,
        'mountpoint': "/storage/{}".format(disk.name),
    }
    fs_service = filesystem_actor.serviceCreate(instance=instance, args=fs_args)
    return fs_service

def create_ardb(storagecluster_service, fs_service, instance, master=None):
    container_actor = storagecluster_service.aysrepo.actorGet('container')
    ardb_actor = storagecluster_service.aysrepo.actorGet('ardb')

    container_args = {
        'node': fs_service.parent.parent.name,
        'hostNetworking': True,
        'filesystems': [fs_service.name],
        'flist': 'https://hub.gig.tech/gig-official-apps/ardb-rocksdb.flist',
        'storage': 'ardb://hub.gig.tech:16379',
        'mounts': ["{}:{}".format(fs_service.name, "/mnt/data")],
        'ports': ['16379:16379'],
    }
    container_service = container_actor.serviceCreate(
        instance=instance,
        args=container_args
    )

    ardb_args = {
        'homeDir': "/mnt/data",
        'bind': '0.0.0.0:16379',  # FIXME: should be 40G network
        'container': container_service.name,
    }
    if master:
        ardb_args['master'] = master.name

    ardb_service = ardb_actor.serviceCreate(
        instance=instance,
        args=ardb_args
    )

    return ardb_service

def init(job):
    service = job.service
    service.model.data.status = 'deploying'
    service.save()

    filesystems = []

    job.logger.info("create storagepool and filesystem services")
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
            fs_service = create_filesystem(service, node_service, name, disk)
            service.consume(fs_service)
            filesystems.append(fs_service)

    if len(filesystems) <= 0:
        raise j.exceptions.RuntimeError(
        "no available disks on node {node}. can't continue to deploy storage cluster {sc}".format(
            node=node_service.name,
            sc=service.name,
        ))

    job.logger.info("distribute data ardb server on all the filesystems available")
    ardb_services = []
    for i in range(service.model.data.nbrServer):
        fs_service = filesystems[i % len(filesystems) - 1]

        name = "{}_data{}".format(service.name, i)
        ardb_service = create_ardb(service, fs_service, name)
        service.consume(ardb_service)
        ardb_services.append(ardb_service)

    job.logger.info("create metadata ardb")
    fs_service = filesystems[(service.model.data.nbrServer + 1) % len(filesystems) - 1]

    name = "{}_metadata0".format(service.name)
    ardb_service = create_ardb(service, fs_service, name)
    service.consume(ardb_service)
    ardb_services.append(ardb_service)

    job.logger.info("deploy slaves for earch master ardb")
    if service.model.data.hasSlave:

        for ardb_service in ardb_services:
            # slave must be on a different node as the master
            master_node = ardb_service.parent.parent
            slave_fs = None
            for fs in filesystems:
                if fs.parent.parent.name != master_node.name:
                    slave_fs = fs

            if slave_fs is None:
                raise j.exceptions.RuntimeError("can't find a node to deploy slave of {}".format(ardb_service))

            ardb_service = create_ardb(
                storagecluster_service=service,
                fs_service=slave_fs,
                instance=ardb_service.parent.name + '_slave',
                master=ardb_service
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
