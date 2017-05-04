

def install(job):
    pass


def start(job):
    from JumpScale.sal.g8os.ARDB import ARDB

    service = job.service
    ardb = ARDB.from_ays(service)
    ardb.start()


def stop(job):
    from JumpScale.sal.g8os.ARDB import ARDB

    service = job.service
    ardb = ARDB.from_ays(service)
    ardb.stop()


def monitor(job):
    from JumpScale.sal.g8os.ARDB import ARDB

    service = job.service
    ardb = ARDB.from_ays(service)

    if service.model.actionsState['install'] == 'ok':
        running, process = ardb.is_running()

        if not running:
            try:
                job.logger.warning("ardb {} not running, trying to restart".format(service.name))
                service.model.dbobj.state = 'error'
                ardb.start()
                running, _ = ardb.is_running()
                if running:
                    service.model.dbobj.state = 'ok'
            except:
                job.logger.error("can't restart ardb {} not running".format(service.name))
                service.model.dbobj.state = 'error'
