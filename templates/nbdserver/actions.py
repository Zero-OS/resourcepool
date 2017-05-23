from JumpScale import j


def get_container(service):
    from JumpScale.sal.g8os.Container import Container
    return Container.from_ays(service.parent)


def is_running(container):
    try:
        for process in container.client.job.list():
            arguments = process['cmd']['arguments']
            if 'name' in arguments and arguments['name'] == '/bin/nbdserver':
                return process
        return False
    except Exception as err:
        if str(err).find("invalid container id"):
            return False
        raise


def install(job):
    from JumpScale.sal.g8os.StorageCluster import StorageCluster
    import time
    import yaml
    import uuid
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


        if  vdiskservice.model.data.storageCluster not in config['storageClusters']:
            storageclusterservice = service.aysrepo.serviceGet(role='storage_cluster',
                                                               instance=vdiskservice.model.data.storageCluster)
            cluster = StorageCluster.from_ays(storageclusterservice)
            clusterconfig = cluster.get_config()
            rootcluster = {'dataStorage': [{'address': rootardb}], 'metadataStorage': {'address': rootardb}}
            rootclustername = hash(j.data.serializer.json.dumps(rootcluster, sort_keys=True))
            vdiskconfig = {'blockSize': vdiskservice.model.data.blocksize,
                           'id': vdiskservice.name,
                           'readOnly': vdiskservice.model.data.readOnly,
                           'size': vdiskservice.model.data.size,
                           'storageCluster': vdiskservice.model.data.storageCluster,
                           'rootStorageCluster': rootclustername,
                           'tlogstoragecluster': vdiskservice.model.data.tlogStoragecluster,
                           'type': str(vdiskservice.model.data.type)}
            config['storageClusters'][cluster.name] = clusterconfig
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
        process = is_running(container)
        container.client.job.kill(process['cmd']['id'], signal=1)

    service.model.data.socketPath = '/server.socket.{id}'.format(id=service.name)
    service.saveAll()


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def stop(job):
    import time
    service = job.service
    container = get_container(service=service)
    process = is_running(container)
    if process:
        job.logger.info("killing process {}".format(process['cmd']['arguments']['name']))
        container.client.process.kill(process['cmd']['id'])

        job.logger.info("wait for nbdserver to stop")
        for i in range(60):
            time.sleep(1)
            if is_running(container):
                continue
            return
        raise j.exceptions.RuntimeError("ardb-server didn't stopped")
