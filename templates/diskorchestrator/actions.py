from js9 import j


def get_container(service):
    from zeroos.orchestrator.sal.Container import Container
    return Container.from_ays(service.parent)


def is_job_running(container, cmd='/bin/nbdserver'):
    try:
        for job in container.client.job.list():
            arguments = job['cmd']['arguments']
            if 'name' in arguments and arguments['name'] == cmd:
                return job
        return False
    except Exception as err:
        if str(err).find("invalid container id"):
            return False
        raise


def is_socket_listening(container, socketpath):
    for connection in container.client.info.port():
        if connection['network'] == 'unix' and connection['unix'] == socketpath:
            return True
    return False


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

    storagecluster_storage_ips = []

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
            config['storageClusters'][storagecluster] = clusterconfig

        if rootclustername not in config['storageClusters']:
            config['storageClusters'][rootclustername] = rootcluster

        vdisk_type = "cache" if str(vdiskservice.model.data.type) == "tmp" else str(vdiskservice.model.data.type)
        vdiskconfig = {'blockSize': vdiskservice.model.data.blocksize,
                       'id': vdiskservice.name,
                       'readOnly': vdiskservice.model.data.readOnly,
                       'size': vdiskservice.model.data.size,
                       'storageCluster': vdiskservice.model.data.storageCluster,
                       'rootStorageCluster': rootclustername,
                       'tlogstoragecluster': vdiskservice.model.data.tlogStoragecluster,
                       'type': vdisk_type}
        config['vdisks'][vdiskservice.name] = vdiskconfig
        storagecluster_storage_ips += [storage['address'] for storage in clusterconfig['dataStorage']]
    start_tlog(service, container, storagecluster_storage_ips)

    yamlconfig = yaml.safe_dump(config, default_flow_style=False)
    configstream = BytesIO(yamlconfig.encode('utf8'))
    configstream.seek(0)
    container.client.filesystem.upload(configpath, configstream)

    if not is_job_running(container):
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
            if is_socket_listening(container, socketpath):
                break
            time.sleep(0.2)
        else:
            raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(service.name))
        # make sure nbd is still running
        running = is_job_running(container)
        for vdisk in vdisks:
            if running:
                vdisk.model.data.status = 'running'
                vdisk.saveAll()
        if not running:
            raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(service.name))
    else:
        # send a siganl sigub(1) to reload the config in case it was changed.
        job = is_job_running(container)
        container.client.job.kill(job['cmd']['id'], signal=1)

    service.model.data.socketPath = socketpath
    service.saveAll()


def start_tlog(service, container, storage_ips):
    if not is_job_running(container, cmd='/bin/tlogserver'):
        storage_ips = ','.join(set(storage_ips))
        container.client.system('/bin/tlogserver -storage-addresses={}'.format(storage_ips))
        if not is_job_running(container, cmd='/bin/tlogserver'):
            raise j.exceptions.RuntimeError("Failed to start tlogserver {}".format(service.name))


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def get_storagecluster_config(service, storagecluster):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
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
    for vdiskservice in vdisks:
        vdiskservice.model.data.status = 'halted'
        vdiskservice.saveAll()
        if vdiskservice.model.data.type == "tmp":
            j.tools.async.wrappers.sync(vdiskservice.executeAction('delete'))

    nbdjob = is_job_running(container)
    if nbdjob:
        job.logger.info("killing job {}".format(nbdjob['cmd']['arguments']['name']))
        container.client.job.kill(nbdjob['cmd']['id'])

        job.logger.info("wait for nbdserver to stop")
        for i in range(60):
            time.sleep(1)
            if is_job_running(container):
                continue
            return
        raise j.exceptions.RuntimeError("nbdserver didn't stopped")


def monitor(job):
    service = job.service
    if not service.model.actionsState['install'] == 'ok':
        return
    vm = service.aysrepo.serviceGet(role='vm', instance=service.name)
    vdisks = vm.producers.get('vdisk', [])
    running = is_job_running(get_container(service))
    for vdisk in vdisks:
        if running:
            vdisk.model.data.status = 'running'
        else:
            vdisk.model.data.status = 'halted'
    vdisk.saveAll()

