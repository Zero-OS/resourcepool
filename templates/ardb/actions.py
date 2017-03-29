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
    # The container has everything needed
    pass

def start(job):
    import time
    service = job.service
    client = service.actions.get_container_client_(service=service)
    # TODO: the flist should be rebuilt with the shared objects under the default location
    resp = client.system('/opt/lib/ld-linux-x86-64.so.2 --library-path /opt/lib /opt/bin/ardb-server /optvar/cfg/ardb.conf')

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
