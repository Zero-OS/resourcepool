from js9 import j


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
    import time
    from zerotier import client
    from zeroos.orchestrator.sal.Container import Container

    service = job.service
    container = Container.from_ays(service)
    container.start()

    if container.is_running():
        service.model.data.status = "running"
    else:
        raise j.exceptions.RuntimeError("container didn't started")

    def wait_for_interface():
        start = time.time()
        while start + 60 > time.time():
            for link in container.client.ip.link.list():
                if link['type'] == 'tun':
                    return
            time.sleep(0.5)
        raise j.exceptions.RuntimeError("Could not find zerotier network interface")

    for nic in service.model.data.nics:
        if nic.type == 'zerotier':
            wait_for_interface()
            service.model.data.zerotiernodeid = container.client.zerotier.info()['address']
            if nic.token:
                zerotier = client.Client()
                zerotier.set_auth_header('bearer {}'.format(nic.token))
                resp = zerotier.network.getMember(service.model.data.zerotiernodeid, nic.id)
                member = resp.json()
                if member['config']['authorized'] is False and member['online']:
                    # authorized new member
                    job.logger.info("authorize new member {} to network {}".format(member['nodeId']), nic.id)
                    member['config']['authorized'] = True
                    zerotier.network.updateMember(member, member['nodeId'], nic.id)

    service.saveAll()


def stop(job):
    from zeroos.orchestrator.sal.Container import Container

    container = Container.from_ays(job.service)
    container.stop()

    if not container.is_running():
        job.service.model.data.status = "halted"
    else:
        raise j.exceptions.RuntimeError("container didn't stopped")


def monitor(job):
    from zeroos.orchestrator.sal.Container import Container
    service = job.service

    if service.model.actionsState['install'] == 'ok':
        container = Container.from_ays(job.service)
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
