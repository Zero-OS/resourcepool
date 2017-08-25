from js9 import j


def get_container(service, password):
    from zeroos.orchestrator.sal.Container import Container
    return Container.from_ays(service.parent, password)


def is_port_listening(container, port, timeout=30, listen=True):
    import time
    start = time.time()
    while start + timeout > time.time():
        if port not in container.node.freeports(port, nrports=3):
            return True
        if not listen:
            return False
        time.sleep(0.2)
    return False


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


def save_config(job, vdisks=None):
    import yaml
    import random
    from zeroos.orchestrator.sal.ETCD import ETCD

    service = job.service
    config = {"servers": [service.model.data.bind]}
    yamlconfig = yaml.safe_dump(config, default_flow_style=False)

    etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
    etcd = random.choice(etcd_cluster.producers['etcd'])

    etcd = ETCD.from_ays(etcd, job.context['token'])
    result = etcd.put(key="%s:cluster:conf:tlog" % service.name, value=yamlconfig)
    if result.state != "SUCCESS":
        raise RuntimeError("Failed to save tlog %s config" % service.name)

    for vdisk in vdisks:
        config = {
            "storageClusterID": vdisk.model.data.storageCluster,
            "templateStorageClusterID": vdisk.model.data.templateStorageCluster or "",
            "tlogServerClusterID": service.name,
            "slaveStorageClusterID": vdisk.model.data.backupStoragecluster or "",
        }
        yamlconfig = yaml.safe_dump(config, default_flow_style=False)
        result = etcd.put(key="%s:vdisk:conf:storage:nbd" % vdisk.name, value=yamlconfig)
        if result.state != "SUCCESS":
            raise RuntimeError("Failed to save nbd conf storage: %s", vdisk.name)


def install(job):
    from zeroos.orchestrator.sal.ETCD import EtcdCluster

    service = job.service

    etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
    etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context['token'])

    vm = service.consumers['vm'][0]
    vdisks = vm.producers.get('vdisk', [])
    container = get_container(service, job.context['token'])
    config = {
        'storageClusters': set(),
        'data-shards': 0,
        'parity-shards': 0,
    }

    backup = False
    for vdiskservice in vdisks:
        objectcluster = vdiskservice.model.data.objectStoragecluster
        if objectcluster and objectcluster not in config['storageClusters']:
            _, data_shards, parity_shards = get_storagecluster_config(job, objectcluster)
            config['storageClusters'].add(objectcluster)
            config['data-shards'] += data_shards
            config['parity-shards'] += parity_shards
            if vdiskservice.model.data.backupStoragecluster:
                backup = True

    if not config['storageClusters']:
        return

    save_config(job, vdisks)
    data_shards = config.pop('data-shards')
    parity_shards = config.pop('parity-shards')

    bind = service.model.data.bind
    if not is_port_listening(container, int(bind.split(':')[1]), listen=False):
        cmd = '/bin/tlogserver \
                -id {id} \
                -address {bind} \
                -data-shards {data_shards} \
                -parity-shards {parity_shards} \
                -config "{dialstrings}" \
                '.format(id=vm.name,
                         bind=bind,
                         data_shards=data_shards,
                         parity_shards=parity_shards,
                         dialstrings=etcd_cluster.dialstrings)
        if backup:
            cmd += '-with-slave-sync'
        job.logger.info("Starting tlog server: %s" % cmd)
        container.client.system(cmd, id="{}.{}".format(service.model.role, service.name))
        if not is_port_listening(container, int(bind.split(":")[1])):
            raise j.exceptions.RuntimeError('Failed to start tlogserver {}'.format(service.name))
    service.model.data.status = 'running'
    service.saveAll()

    tcpsrv = service.producers['tcp'][0]
    if tcpsrv.model.data.status == "dropped":
        j.tools.async.wrappers.sync(tcpsrv.executeAction('install', context=job.context))


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install', context=job.context))


def get_storagecluster_config(job, storagecluster):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    storageclusterservice = job.service.aysrepo.serviceGet(role='storage_cluster',
                                                           instance=storagecluster)
    cluster = StorageCluster.from_ays(storageclusterservice, job.context['token'])
    return cluster.get_config(), cluster.data_shards, cluster.parity_shards


def stop(job):
    import time
    service = job.service
    if service.model.data.status != 'running':
        return

    service.model.data.status = 'halting'
    service.saveAll()
    container = get_container(service, job.context['token'])
    bind = service.model.data.bind
    port = int(bind.split(':')[1])
    tlogjob = is_job_running(container)
    if tlogjob:
        job.logger.info("killing job {}".format(tlogjob['cmd']['arguments']['name']))
        container.client.job.kill(tlogjob['cmd']['id'])

        job.logger.info("wait for tlogserver to stop")
        for i in range(60):
            time.sleep(1)
            if not is_port_listening(container, port):
                break
            raise j.exceptions.RuntimeError("Failed to stop Tlog server")
    service.model.data.status = 'halted'
    service.saveAll()

    tcpsrv = service.producers['tcp'][0]
    if tcpsrv.model.data.status == "opened":
        j.tools.async.wrappers.sync(tcpsrv.executeAction('drop', context=job.context))


def monitor(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    if not service.model.actionsState['install'] == 'ok':
        return

    if str(service.model.data.status) != 'running':
        return

    bind = service.model.data.bind
    port = int(bind.split(':')[1])
    container = get_container(service, get_jwt_token(job.service.aysrepo))
    if is_port_listening(container, port):
        return

    j.tools.async.wrappers.sync(service.executeAction('start', context={"token": get_jwt_token(job.service.aysrepo)}))


def watchdog_handler(job):
    import asyncio
    loop = j.atyourservice.server.loop
    service = job.service
    if str(service.model.data.status) != 'running':
        return
    eof = job.model.args['eof']
    if eof:
        asyncio.ensure_future(service.executeAction('start', context=job.context), loop=loop)
