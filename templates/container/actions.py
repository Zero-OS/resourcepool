from JumpScale import j


def input(job):
    # make sure we always consume all the filesystems used in the mounts property
    args = job.model.args
    mounts = args.get('mounts', [])
    if 'filesystems' in args:
        raise j.exceptions.InputError("Filesystem should not be passed from the blueprint")
    args['filesystems'] = []
    filesystems = args['filesystems']
    for mount in mounts:
        if mount['filesystem'] not in filesystems:
            args['filesystems'].append(mount['filesystem'])

    args['bridges'] = []
    for nic in args.get('nics', []):
        if nic['type'] == 'bridge':
            args['bridges'].append(nic['id'])

    return args


def install(job):
    job.service.model.data.status = "halted"
    j.tools.async.wrappers.sync(job.service.executeAction('start'))


def start(job):
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None
    )

    container = node.containers.get(service.name)
    container.start()

    if container.is_running():
        job.service.model.data.status = "running"
    else:
        raise j.exceptions.RuntimeError("container didn't started")


def stop(job):
    service = job.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisAddr,
        port=service.model.data.redisPort,
        password=service.model.data.redisPassword or None
    )

    container = node.containers.get(service.name)
    container.stop()

    if not container.is_running():
        job.service.model.data.status = "halted"
    else:
        raise j.exceptions.RuntimeError("container didn't stopped")


def monitor(job):
    service = job.service

    if service.model.actionsState['install'] == 'ok':
        service = job.service
        node = j.sal.g8os.get_node(
            addr=service.model.data.redisAddr,
            port=service.model.data.redisPort,
            password=service.model.data.redisPassword or None
        )

        container = node.containers.get(service.name)
        running = container.is_running()
        if not running and service.model.data.status == 'running':
            try:
                job.logger.warning("container {} not running, trying to restart".format(service.name))
                service.model.dbobj.state = 'error'
                container.start()

                if container.is_running():
                    service.model.dbobj.state = 'ok'
            except:
                job.logger.error("can't restart container {} not running".format(service.name))
                service.model.dbobj.state = 'error'
        elif running and service.model.data.status == 'halted':
            try:
                job.logger.warning("container {} running, trying to stop".format(service.name))
                service.model.dbobj.state = 'error'
                container.stop()
                running, _ = container.is_running()
                if not running:
                    service.model.dbobj.state = 'ok'
            except:
                job.logger.error("can't stop container {} is running".format(service.name))
                service.model.dbobj.state = 'error'
