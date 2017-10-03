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
    j.tools.async.wrappers.sync(service.executeAction('install', context=job.context))


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
        j.tools.async.wrappers.sync(vdiskservice.executeAction('pause'))
        if vdiskservice.model.data.type == "tmp":
            j.tools.async.wrappers.sync(vdiskservice.executeAction('delete', context=job.context))

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
        raise j.exceptions.RuntimeError("nbdserver didn't stop")
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
            j.tools.async.wrappers.sync(vdisk.executeAction('start'))
        else:
            j.tools.async.wrappers.sync(vdisk.executeAction('pause'))


def ardb_message(job, message):
    # status = message['status']
    # do we need to check the status ?
    import asyncio
    loop = j.atyourservice.server.loop

    service = job.service
    vdisk_id = message['data']['vdiskID']
    vdisks = service.aysrepo.servicesFind(name=vdisk_id, role='vdisk')
    job.logger.info("found %d disks to recover", len(vdisks))
    for vdisk in vdisks:
        # NOTE: this should match 1 vdisk at max
        job.logger.info("calling recover for disk %s" % vdisk_id)
        vdisk_storage = vdisk.parent
        asyncio.ensure_future(
            vdisk_storage.executeAction('recover', args={'message': message}, context=job.context),
            loop=loop
        )


def handle_messages(job, message):
    """ message == {"status":422,"subject":"ardb","data":{"address":"172.17.0.255:2000","db":0,"type":"primary","vdiskID":"vd6"}}"""
    job.logger.info('processing nbdserver message "%s"', message)
    switch = {
        'ardb': ardb_message,
    }

    handler = switch.get(message['subject'])
    if handler is not None:
        return handler(job, message)


def debug_failure(job):
    handle_messages(job, {
        "status":422,
        "subject":"ardb",
        "data": {
            "address":"172.17.0.255:2000",
            "db":0,
            "type":"primary",
            "vdiskID":"vd0"
        }
    })


def watchdog_handler(job):
    import asyncio
    loop = j.atyourservice.server.loop
    service = job.service
    if str(service.model.data.status) != 'running':
        return

    eof = job.model.args['eof']
    service = job.service
    if eof:
        job.logger.warning("##### nbdserver exited (got eof)")
        vm_service = service.consumers['vm'][0]
        asyncio.ensure_future(vm_service.executeAction('stop', context=job.context, args={"cleanup": False}), loop=loop)
        #TODO: starting the machine on eof is not a good idea because it can conflict with a running recovery
        #TODO: process. Since each message runns the watchdog_handler in a separate concurrent job we can not depend
        #TODO: on the messages order.
        #TODO: may be report this to the user somehow so he can start it again if he wants.
        return

    message = job.model.args.get('message')
    level = job.model.args.get('level')
    job.logger.info('level: %d message: %s' % (level, message))
    if level == 20: #json message
        return handle_messages(job,
            j.data.serializer.json.loads(message)
        )
