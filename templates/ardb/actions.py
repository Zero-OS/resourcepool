from JumpScale import j


def install(job):
    j.tools.async.wrappers.sync(job.service.executeAction('start'))


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

    if service.model.actionsState['install'] == 'ok':
        ardb = ARDB.from_ays(service)
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
