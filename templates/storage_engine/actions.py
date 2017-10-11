from js9 import j


def install(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    job.service.executeAction('start', context=job.context)


def start(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    storageEngine = StorageEngine.from_ays(service, job.context['token'])
    storageEngine.start()
    service.model.data.status = 'running'


def stop(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    service.model.data.status = 'halting'
    service.saveAll()
    storageEngine = StorageEngine.from_ays(service, job.context['token'])
    storageEngine.stop()
    service.model.data.status = 'halted'


def monitor(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service

    if service.model.actionsState["install"] == "ok":
        storageEngine = StorageEngine.from_ays(service, get_jwt_token(service.aysrepo))
        running, process = storageEngine.is_running()

        if running:
            if not storageEngine.is_healthy():
                service.model.data.status = "unhealthy"
            else:
                service.model.data.status = "running"


def watchdog_handler(job):
    import asyncio
    service = job.service

    if service.model.data.status != "running":
        return

    loop = j.atyourservice.server.loop
    eof = job.model.args["eof"]
    if eof:
        asyncio.ensure_future(service.asyncExecuteAction("start", context=job.context), loop=loop)
