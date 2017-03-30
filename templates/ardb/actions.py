def get_container_client_(service):
    return service.parent.actions.get_container_client_(service=service.parent)

def is_ardb_running_(client):
    try:
        for process in client.process.list():
            if process['cmd']['arguments']['name'] == '/opt/bin/ardb-server':
                return process
        return False
    except Exception as err:
        if str(err).find("invalid container id"):
            return False
        raise

def install(job):
    import io
    service = job.service
    client = service.actions.get_container_client_(service=service)
    job.logger.info("get template config")
    # download template cfg

    buff = io.BytesIO()
    client.filesystem.download('/etc/ardb.conf', buff)
    content = buff.getvalue().decode()

    # update config
    job.logger.info("update config")
    content = content.replace('/opt/ardb', service.model.data.homeDir)
    content = content.replace('0.0.0.0:16379', '{host}:{port}'.format(host=service.model.data.host, port=service.model.data.port))

    if service.model.data.master != '' and service.producers.get('master', None) is not None:
        master = service.producers['master'][0] # it can only have one
        content = content.replace('#slaveof 127.0.0.1:6379', 'slaveof {host}:{port}'.format(host=master.model.data.host, port=master.model.data.port))

    # make sure home directory exists
    client.bash('mkdir -p {}'.format(service.model.data.homeDir))

    # upload new config
    job.logger.info("send new config to g8os")
    client.filesystem.upload('/etc/ardb.conf', io.BytesIO(initial_bytes=content.encode()))

def start(job):
    import time
    service = job.service
    client = service.actions.get_container_client_(service=service)

    resp = client.system('/bin/ardb-server /etc/ardb.conf')

    # wait for ardb to start
    for i in range(60):
        if not service.actions.is_ardb_running_(client):
            time.sleep(1)
        else:
            return

    raise j.exceptions.RuntimeError("ardb-server didn't started: {}".format(resp.get()))


def stop(job):
    import time
    service = job.service
    client = service.actions.get_container_client_(service=service)
    process = service.actions.is_ardb_running_(client)
    if process:
        job.logger.info("killing process {}".format(process['cmd']['arguments']['name']))
        client.process.kill(process['cmd']['id'])

        job.logger.info("wait for ardb to stop")
        for i in range(60):
            time.sleep(1)
            if service.actions.is_ardb_running_(client):
                time.sleep(1)
            else:
                return
        raise j.exceptions.RuntimeError("ardb-server didn't stopped")

def monitor(job):
    service = job.service
    client = service.actions.get_container_client_(service=service)
    process = service.actions.is_ardb_running_(client)
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
