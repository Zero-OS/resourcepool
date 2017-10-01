from js9 import j


def install(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    j.tools.async.wrappers.sync(job.service.executeAction('start', context=job.context))


def start(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    if service.model.data.status == 'broken':
        job.logger.error('storage_engine "%s" is marked as broken not starting' % service.name)
        return

    service.model.data.enabled = True
    service.saveAll()
    storageEngine = StorageEngine.from_ays(service, job.context['token'])
    storageEngine.start()

    if not storageEngine.is_healthy():
        service.model.data.status = 'broken'
        service.saveAll()
        raise RuntimeError('storage_engine "%s" is flagged as broken' % service.name)
    else:
        service.model.data.status = 'running'

    service.saveAll()


def stop(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    service.model.data.enabled = False
    service.saveAll()
    storageEngine = StorageEngine.from_ays(service, job.context['token'])
    storageEngine.stop()

    service.model.data.status = 'halted'


def monitor(job):
    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    if service.model.actionsState['install'] != 'ok':
        return

    if service.model.data.status != 'running':
        return

    storageEngine = StorageEngine.from_ays(service, get_jwt_token(service.aysrepo))
    running, process = storageEngine.is_running()
    if not running:
        service.model.data.status = 'halted'

    if not storageEngine.is_healthy():
        service.model.data.status = 'broken'


def watchdog_handler(job):
    return #debug
    import asyncio
    service = job.service
    if not service.model.data.enabled:
        return

    loop = j.atyourservice.server.loop
    eof = job.model.args['eof']
    if eof:
        asyncio.ensure_future(job.service.executeAction('start', context=job.context), loop=loop)
