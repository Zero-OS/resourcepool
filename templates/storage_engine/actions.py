from js9 import j


def install(job):
    j.tools.async.wrappers.sync(job.service.executeAction('start', context=job.context))


def start(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine

    service = job.service
    storageEngine = StorageEngine.from_ays(service, job.context['token'])
    storageEngine.start()
    service.model.data.status = 'running'


def stop(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine

    service = job.service
    storageEngine = StorageEngine.from_ays(service, job.context['token'])
    storageEngine.stop()
    service.model.data.status = 'halted'


def monitor(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service

    if service.model.actionsState['install'] == 'ok':
        storageEngine = StorageEngine.from_ays(service, get_jwt_token(service.aysrepo))
        running, process = storageEngine.is_running()

        if not running:
            try:
                job.logger.warning("storageEngine {} not running, trying to restart".format(service.name))
                service.model.dbobj.state = 'error'
                storageEngine.start()
                running, _ = storageEngine.is_running()
                if running:
                    service.model.dbobj.state = 'ok'
                    service.model.data.status = 'running'
            except:
                job.logger.error("can't restart storageEngine {} not running".format(service.name))
                service.model.dbobj.state = 'error'
                service.model.data.status = 'halted'
        else:
            if not storageEngine.is_healthy():
                service.model.data.status = "unhealthy"
