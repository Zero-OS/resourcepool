from js9 import j


def get_container(service):
    from zeroos.orchestrator.sal.Container import Container
    return Container.from_ays(service.parent)


def is_job_running(container, cmd='/bin/tlogserver'):
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


def is_port_listening(container, port):
    for connection in container.client.info.port():
        if connection['network'] == 'tcp' and connection['port'] == port:
            return True
    return False


def install(job):
    import time
    import yaml
    from io import BytesIO
    service = job.service
    vm = service.aysrepo.serviceGet(role='vm', instance=service.name)
    vdisks = vm.producers.get('vdisk', [])
    container = get_container(service)
    config = {
        'vdisks': {},
        'storageClusters': {},
        'k': 0,
        'm': 0,
    }

    for vdiskservice in vdisks:
        tlogcluster = vdiskservice.model.data.tlogStoragecluster
        if tlogcluster and tlogcluster not in config['storageClusters']:
            clusterconfig, k, m = get_storagecluster_config(service, tlogcluster)
            config['storageClusters'][tlogcluster] = {"dataStorage": clusterconfig["dataStorage"]}
            config['vdisks'][vdiskservice.name] = {'tlogStorageCluster': tlogcluster}
            config['k'] += k
            config['m'] += m

    k = config.pop('k')
    m = config.pop('m')

    configpath = "/tlog_{}.config".format(service.name)
    yamlconfig = yaml.safe_dump(config, default_flow_style=False)
    configstream = BytesIO(yamlconfig.encode('utf8'))
    configstream.seek(0)
    container.client.filesystem.upload(configpath, configstream)
    if not is_job_running(container, cmd='/bin/tlogserver'):
        ip = container.node.storageAddr
        port = container.node.freeports(baseport=11211, nrports=1)[0]
        logpath = '/tlog_{}.log'.format(service.name)
        container.client.system(
                '/bin/tlogserver \
                -address {ip}:{port} \
                -k {k} \
                -m {m} \
                -logfile {log} \
                -config {config}'
                .format(ip=ip,
                        port=port,
                        config=configpath,
                        k=k,
                        m=m,
                        log=logpath)
            )
        if not is_job_running(container, cmd='/bin/tlogserver'):
            raise j.exceptions.RuntimeError("Failed to start tlogserver {}".format(service.name))
        service.model.data.bind = '%s:%s' % (ip, port)
        # container.node.client.nft.open_port(port)
        # Ensure tlog is running
        start = time.time()
        while start + 60 > time.time():
            if is_port_listening(container, port):
                break
            time.sleep(0.2)
        else:
            raise j.exceptions.RuntimeError("Failed to start tlogserver {}".format(service.name))
        # make sure tlog is still running
        running = is_job_running(container)
        for vdisk in vdisks:
            if running:
                vdisk.model.data.status = 'running'
                vdisk.saveAll()
        if not running:
            container.node.client.nft.drop_port(port)
            raise j.exceptions.RuntimeError("Failed to start tlogserver {}".format(service.name))
    else:
        # send a siganl sigub(1) to reload the config in case it was changed.
        job = is_job_running(container)
        print(job)
        container.client.job.kill(job['cmd']['id'], signal=1)


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))


def get_storagecluster_config(service, storagecluster):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    storageclusterservice = service.aysrepo.serviceGet(role='storage_cluster',
                                                       instance=storagecluster)
    cluster = StorageCluster.from_ays(storageclusterservice)
    return cluster.get_config(), cluster.k, cluster.m


def stop(job):
    import time
    service = job.service
    container = get_container(service=service)

    tlogjob = is_job_running(container)
    if tlogjob:
        job.logger.info("killing job {}".format(tlogjob['cmd']['arguments']['name']))
        container.client.job.kill(tlogjob['cmd']['id'])

        job.logger.info("wait for tlogserver to stop")
        for i in range(60):
            time.sleep(1)
            if is_job_running(container):
                continue
            return
        raise j.exceptions.RuntimeError("tlogserver didn't stopped")
