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
        if not running:
            raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(vm.name))

        vdisk_state = {}
        for vdisk in vdisks:
            # warmming up nbdserver manually. we send a qemu-ing info so the nbdserver already start doing the requests task in order to be ready to
            # serve the vdisks
            #cmd = 'qemu-img info nbd:unix:/mnt/container-{container_id}{socket_path}:exportname={vdisk_id}'.format(container_id=container.id, socket_path=socketpath, vdisk_id=vdisk.name)
            #job.logger.debug("Executing cmd '%s' to warm up nbdserver for '%s'.", cmd, service.name)
            #resp = container.node.client.system(cmd).get()
            #start = time.time()
            #timeout = 300
            #while resp.state != 'SUCCESS' or (time.time() - start) > timeout:
            #    job.logger.debug("%s\n%s\n%s", cmd, resp.stdout, resp.stderr)
            #    time.sleep(0.5)
            #    resp = container.node.client.system(cmd).get()
            #if resp.state != 'SUCCESS':
            #    running = False
            if running:
                vdisk.model.data.status = 'running'
                vdisk.saveAll()
            else:
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
    import signal

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    container = get_container(service, job.context['token'])

    force_stop = job.model.args.get("force_stop", False)
    max_wait = 10 if force_stop else 60

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
        pid = nbdjob['cmd']['id']
        job.logger.info("killing job {}".format(nbdjob['cmd']['arguments']['name']))
        container.client.job.kill(pid)

        job.logger.info("wait for nbdserver to stop")
        for i in range(max_wait):
            time.sleep(1)
            if is_job_running(container, socket=service.model.data.socketPath):
                continue
            return

        # if we couldn't stop the process gently, just kill it
        container.client.job.kill(pid, signal=signal.SIGKILL)

        if is_job_running(container, socket=service.model.data.socketPath):
            raise j.exceptions.RuntimeError("nbdserver %s didn't stop" % service.model.name)

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


def ardb_message(job, message):
    # status = message['status']
    # do we need to check the status ?
    service = job.service
    vdisk_id = message['data']['vdiskID']
    vdisks = service.aysrepo.servicesFind(name=vdisk_id, role='vdisk')
    job.logger.info("found %d disks to recover", len(vdisks))
    for vdisk in vdisks:
        # NOTE: this should match 1 vdisk at max
        job.logger.info("calling recover for disk %s" % vdisk_id)
        vdisk_storage = vdisk.parent
        vdisk_storage.executeAction('recover', args={'message': message}, context=job.context)


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
    message = job.model.args.get('message')
    level = job.model.args.get('level')

    job.logger.info('level: %d message: %s' % (level, message))
    if level == 20:
        return handle_messages(job, j.data.serializer.json.loads(message))

