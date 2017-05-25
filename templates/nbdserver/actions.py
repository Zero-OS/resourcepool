from JumpScale import j


def get_container(service):
    from JumpScale.sal.g8os.Container import Container
    return Container.from_ays(service.parent)


def is_running(container):
    try:
        for job in container.client.job.list():
            arguments = job['cmd']['arguments']
            if 'name' in arguments and arguments['name'] == '/bin/nbdserver':
                return job
        return False
    except Exception as err:
        if str(err).find("invalid container id"):
            return False
        raise


def install(job):
    import time
    import yaml
    from io import BytesIO
    from urllib.parse import urlparse
    service = job.service
    vm = service.aysrepo.serviceGet(role='vm', instance=service.name)
    vdisks = vm.producers.get('vdisk', [])
    container = get_container(service)
    config = {
        'storageClusters': {},
        'vdisks': {}
    }
    socketpath = '/server.socket.{id}'.format(id=service.name)
    configpath = "/{}.config".format(service.name)
    for vdiskservice in vdisks:
        template = urlparse(vdiskservice.model.data.templateVdisk)
        if template.scheme == 'ardb' and template.netloc:
            rootardb = template.netloc
        else:
            conf = container.node.client.config.get()
            rootardb = urlparse(conf['globals']['storage']).netloc

        if vdiskservice.model.data.storageCluster not in config['storageClusters']:
            storagecluster = vdiskservice.model.data.storageCluster
            clusterconfig = get_storagecluster_config(service, storagecluster)
            rootcluster = {'dataStorage': [{'address': rootardb}], 'metadataStorage': {'address': rootardb}}
            rootclustername = hash(j.data.serializer.json.dumps(rootcluster, sort_keys=True))
            vdisk_type = "cache" if str(vdiskservice.model.data.type) == "tmp" else str(vdiskservice.model.data.type)
            vdiskconfig = {'blockSize': vdiskservice.model.data.blocksize,
                           'id': vdiskservice.name,
                           'readOnly': vdiskservice.model.data.readOnly,
                           'size': vdiskservice.model.data.size,
                           'storageCluster': storagecluster,
                           'rootStorageCluster': rootclustername,
                           'tlogstoragecluster': vdiskservice.model.data.tlogStoragecluster,
                           'type': vdisk_type}
            config['storageClusters'][storagecluster] = clusterconfig
        if rootclustername not in config['storageClusters']:
            config['storageClusters'][rootclustername] = rootcluster
        config['vdisks'][vdiskservice.name] = vdiskconfig

    yamlconfig = yaml.safe_dump(config, default_flow_style=False)
    configstream = BytesIO(yamlconfig.encode('utf8'))
    configstream.seek(0)
    container.client.filesystem.upload(configpath, configstream)

    if not is_running(container):
        container.client.system(
            '/bin/nbdserver \
            -protocol unix \
            -address "{socketpath}" \
            -config {config}'
            .format(id=service.name, socketpath=socketpath, config=configpath)
        )
        # wait for socket to be created
        start = time.time()
        while start + 60 > time.time():
            if container.client.filesystem.exists(socketpath):
                break
            else:
                time.sleep(0.2)
        else:
            raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(service.name))
        # make sure nbd is still running
        if not is_running(container):
            raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(service.name))
    else:
        # send a siganl sigub(1) to reload the config in case it was changed.
        job = is_running(container)
        container.client.job.kill(job['cmd']['id'], signal=1)

    service.model.data.socketPath = '/server.socket.{id}'.format(id=service.name)
    service.saveAll()


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def get_storagecluster_config(service, storagecluster):
    from JumpScale.sal.g8os.StorageCluster import StorageCluster
    storageclusterservice = service.aysrepo.serviceGet(role='storage_cluster',
                                                       instance=storagecluster)
    cluster = StorageCluster.from_ays(storageclusterservice)
    return cluster.get_config()


def stop(job):
    import time
    service = job.service
    container = get_container(service=service)

    vm = service.aysrepo.serviceGet(role='vm', instance=service.name)
    vdisks = vm.producers.get('vdisk', [])

    # Delete tmp vdisks
    configpath = "/{}.config".format(service.name)
    vdisks = [vdiskservice.name for vdiskservice in vdisks if vdiskservice.model.data.type == "tmp"]
    container.client.system(
        '/bin/g8stor \
        delete \
        vdisks \
        {vdisks} \
        --config {configpath}'
        .format(vdisks=" ".join(vdisks), configpath=configpath)
    )

    nbdjob = is_running(container)
    if nbdjob:
        job.logger.info("killing job {}".format(nbdjob['cmd']['arguments']['name']))
        container.client.job.kill(nbdjob['cmd']['id'])

        job.logger.info("wait for nbdserver to stop")
        for i in range(60):
            time.sleep(1)
            if is_running(container):
                continue
            return
        raise j.exceptions.RuntimeError("nbdserver didn't stopped")
