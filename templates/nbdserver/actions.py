from js9 import j


def get_container(service, password):
    from zeroos.orchestrator.sal.Container import Container
    return Container.from_ays(service.parent, password, logger=service.logger)


def is_job_running(container, cmd='/bin/nbdserver', socket=None):
    try:
        for job in container.client.job.list():
            arguments = job['cmd']['arguments']
            if 'name' in arguments and arguments['name'] == cmd:
                if not socket or socket in arguments['args']:
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
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    import time
    service = job.service

    vm = service.consumers['vm'][0]
    vdisks = vm.producers.get('vdisk', [])
    container = get_container(service, job.context['token'])

    socketpath = '/server.socket.{id}'.format(id=vm.name)

    if not is_job_running(container, socket=socketpath):
        etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
        etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context['token'])
        cmd = '/bin/nbdserver \
            -protocol unix \
            -address "{socketpath}" \
            -id "{id}" \
            -config "{dialstrings}" \
            '.format(socketpath=socketpath, id=vm.name, dialstrings=etcd_cluster.dialstrings)
        job.logger.info("Starting nbd server: %s" % cmd)
        container.client.system(cmd, id="{}.{}".format(service.model.role, service.name))

        # wait for socket to be created
        start = time.time()
        while start + 60 > time.time():
            if is_socket_listening(container, socketpath):
                break
            time.sleep(0.2)
        else:
            raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(vm.name))
        # make sure nbd is still running
        running = is_job_running(container, socket=socketpath)
        for vdisk in vdisks:
            if running:
                vdisk.model.data.status = 'running'
                vdisk.saveAll()
        if not running:
            raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(vm.name))

        service.model.data.socketPath = socketpath
        service.model.data.status = 'running'
        service.saveAll()


def start(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    service.executeAction('install', context=job.context)


def get_storagecluster_config(job, storagecluster):
    from zeroos.orchestrator.configuration import get_jwt_token
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    storageclusterservice = job.service.aysrepo.serviceGet(role='storage_cluster',
                                                           instance=storagecluster)
    cluster = StorageCluster.from_ays(storageclusterservice, job.context['token'])
    return cluster.get_config()


def stop(job):
    from zeroos.orchestrator.configuration import get_jwt_token
    import time

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    container = get_container(service, job.context['token'])

    vm = service.consumers['vm'][0]
    vdisks = vm.producers.get('vdisk', [])
    service.model.data.status = 'halting'
    service.saveAll()
    # Delete tmp vdisks
    for vdiskservice in vdisks:
        vdiskservice.executeAction('pause')
        if vdiskservice.model.data.type == "tmp":
            vdiskservice.executeAction('delete', context=job.context)

    nbdjob = is_job_running(container, socket=service.model.data.socketPath)
    if nbdjob:
        job.logger.info("killing job {}".format(nbdjob['cmd']['arguments']['name']))
        container.client.job.kill(nbdjob['cmd']['id'])

        job.logger.info("wait for nbdserver to stop")
        for i in range(60):
            time.sleep(1)
            if is_job_running(container, socket=service.model.data.socketPath):
                continue
            return
        raise j.exceptions.RuntimeError("nbdserver didn't stopped")
    service.model.data.status = 'halted'
    service.saveAll()


def monitor(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    if not service.model.actionsState['install'] == 'ok':
        return

    if str(service.parent.model.data.status) != 'running':
        return
    vm = service.consumers['vm'][0]
    vdisks = vm.producers.get('vdisk', [])
    container = get_container(service, get_jwt_token(job.service.aysrepo))
    running = is_job_running(container, socket=service.model.data.socketPath)
    for vdisk in vdisks:
        if running:
            vdisk.executeAction('start')
        else:
            vdisk.executeAction('pause')


def watchdog_handler(job):
    import asyncio
    loop = j.atyourservice.server.loop
    service = job.service
    if str(service.model.data.status) != 'running':
        return
    eof = job.model.args['eof']
    service = job.service
    if eof:
        vm_service = service.consumers['vm'][0]
        asyncio.ensure_future(vm_service.asyncExecuteAction('stop', context=job.context, args={"cleanup": False}), loop=loop)
        asyncio.ensure_future(vm_service.asyncExecuteAction('start', context=job.context), loop=loop)
