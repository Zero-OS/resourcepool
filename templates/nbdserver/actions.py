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
    import time
    from urllib.parse import urlparse
    service = job.service

    services = service.aysrepo.servicesFind(role='grid_config')
    if len(services) <= 0:
        raise j.exceptions.NotFound("not grid_config service installed. {} can't get the grid API URL.".format(service))

    grid_addr = services[0].model.data.apiURL

    container = get_container(service)
    config = container.node.client.config.get()
    rootardb = urlparse(config['globals']['storage']).netloc
    socketpath = '/server.socket.{id}'.format(id=service.name)
    if not is_running(container, service.name):
        container.client.system(
            '/bin/nbdserver \
            -protocol unix \
            -address "{socketpath}" \
            -export {id} \
            -rootardb {rootardb} \
            -gridapi {api}'
            .format(id=service.name, api=grid_addr, socketpath=socketpath, rootardb=rootardb)
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
    if not is_running(container, service.name):
        raise j.exceptions.RuntimeError("Failed to start nbdserver {}".format(service.name))

    service.model.data.socketPath = '/server.socket.{id}'.format(id=service.name)


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
