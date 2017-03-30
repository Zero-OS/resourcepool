def get_container_client(service):
    cl = j.clients.g8core.get(host=service.parent.parent.model.data.redisAddr,
                              port=service.parent.parent.model.data.redisPort,
                              password=service.parent.parent.model.data.redisPassword)
    return cl.container.client(service.parent.model.data.id)

def is_ardb_running(client):
    try:
        for process in client.process.list():
            if process['cmd']['arguments']['name'] == '/bin/ardb-server':
                return process
        return False
    except Exception as err:
        if str(err).find("invalid container id"):
            return False
        raise

def install(job):
    import io
    service = job.service
    client = get_container_client(service=service)
    job.logger.info("get template config")
    # download template cfg

    buff = io.BytesIO()
    client.filesystem.download('/etc/ardb.conf', buff)
    content = buff.getvalue().decode()

    # update config
    job.logger.info("update config")
    content = content.replace('/mnt/data', service.model.data.homeDir)
    content = content.replace('0.0.0.0:16379', service.model.data.bind)

    if service.model.data.master != '' and service.producers.get('master', None) is not None:
        master = service.producers['master'][0] # it can only have one
        content = content.replace('#slaveof 127.0.0.1:6379', 'slaveof {host}:{port}'.format(host=master.model.data.host, port=master.model.data.port))

    # make sure home directory exists
    client.filesystem.mkdir(service.model.data.homeDir)

    # upload new config
    job.logger.info("send new config to g8os")
    client.filesystem.upload('/etc/ardb.conf', io.BytesIO(initial_bytes=content.encode()))

    j.tools.async.wrappers.sync(service.executeAction('start'))

def start(job):
    import time
    service = job.service
    client = get_container_client(service=service)

    resp = client.system('/bin/ardb-server /etc/ardb.conf')

    # wait for ardb to start
    for i in range(60):
        if not is_ardb_running(client):
            time.sleep(1)
        else:
            return

    raise j.exceptions.RuntimeError("ardb-server didn't started: {}".format(resp.get()))


def stop(job):
    import time
    service = job.service
    client = get_container_client(service=service)
    process = is_ardb_running(client)
    if process:
        job.logger.info("killing process {}".format(process['cmd']['arguments']['name']))
        client.process.kill(process['cmd']['id'])

        job.logger.info("wait for ardb to stop")
        for i in range(60):
            time.sleep(1)
            if is_ardb_running(client):
                time.sleep(1)
            else:
                return
        raise j.exceptions.RuntimeError("ardb-server didn't stopped")

def monitor(job):
    service = job.service
    client = get_container_client(service=service)
    process = is_ardb_running(client)
    if not process:
        try:
            job.logger.warning("ardb {} not running, trying to restart".format(service.name))
            service.model.dbobj.state = 'error'
            j.tools.async.wrappers.sync(service.executeActionJob('start'))
            service.model.dbobj.state = 'ok'
        except:
            job.logger.error("can't restart ardb {} not running".format(service.name))
            service.model.dbobj.state = 'error'
        finally:
            service.saveAll()
