from JumpScale import j


def get_container(service):
    from JumpScale.sal.g8os.Container import Container
    return Container.from_ays(service.parent)


def is_running(container, key):
    try:
        for process in container.client.job.list():
            arguments = process['cmd']['arguments']
            if 'name' in arguments and arguments['name'] == '/bin/nbdserver' and \
               key in arguments['args']:
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

    vdiskservice = service.aysrepo.serviceGet(role='vdisk', instance=service.name)
    container = get_container(service)
    template = urlparse(vdiskservice.model.data.templateVdisk)
    if template.scheme == 'ardb' and template.netloc:
        rootardb = template.netloc
    else:
        config = container.node.client.config.get()
        rootardb = urlparse(config['globals']['storage']).netloc
    socketpath = '/server.socket.{id}'.format(id=service.name)
    if not is_running(container, service.name):
        configpath = "/{}.config".format(service.name)
        storageclusterservice = service.aysrepo.serviceGet(role='storage_cluster', instance=vdiskservice.model.data.storageCluster)
        cluster = StorageCluster.from_ays(storageclusterservice)
        clusterconfig = cluster.get_config()
        rootclustername = str(uuid.uuid4())
        rootcluster = {'dataStorage': [rootardb], 'metadataStorage': rootardb}
        vdiskconfig = {'blockSize': vdiskservice.model.data.blocksize,
                       'id': vdiskservice.name,
                       'readOnly': vdiskservice.model.data.readOnly,
                       'size': vdiskservice.model.data.size,
                       'storageCluster': vdiskservice.model.data.storageCluster,
                       'rootStorageCluster': rootclustername,
                       'tlogstoragecluster': vdiskservice.model.data.tlogStoragecluster,
                       'type': str(vdiskservice.model.data.type)}
        config = {'storageClusters': {cluster.name: clusterconfig,
                                      rootclustername: rootcluster},
                  'vdisks': {vdiskservice.name: vdiskconfig}}
        yamlconfig = yaml.safe_dump(config, default_flow_style=False)
        configstream = BytesIO(yamlconfig.encode('utf8'))
        configstream.seek(0)
        container.client.filesystem.upload(configpath, configstream)

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
    if not is_running(container, configpath):
        raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(service.name))

    service.model.data.socketPath = '/server.socket.{id}'.format(id=service.name)
    service.saveAll()


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def stop(job):
    import time
    service = job.service
    container = get_container(service=service)
    process = is_running(container, service.model.key)
    if process:
        job.logger.info("killing process {}".format(process['cmd']['arguments']['name']))
        container.client.process.kill(process['cmd']['id'])

        job.logger.info("wait for nbdserver to stop")
        for i in range(60):
            time.sleep(1)
            if is_running(container, service.model.key):
                continue
            return
        raise j.exceptions.RuntimeError("ardb-server didn't stopped")
