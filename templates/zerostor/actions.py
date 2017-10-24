from js9 import j


def install(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    job.service.executeAction('start', context=job.context)


def start(job):
    from zeroos.orchestrator.sal.ZeroStor import ZeroStor
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    storageEngine = ZeroStor.from_ays(service, job.context['token'])
    storageEngine.start()
    service.model.data.status = 'running'


def stop(job):
    from zeroos.orchestrator.sal.ZeroStor import ZeroStor
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    service.model.data.status = 'halting'
    service.saveAll()

    zerostor = ZeroStor.from_ays(service, job.context['token'])
    zerostor.stop()
    service.model.data.status = 'halted'
    service.saveAll()


def watchdog_handler(job):
    import asyncio
    service = job.service
    if service.model.data.status != 'running':
        return

    loop = j.atyourservice.server.loop
    eof = job.model.args['eof']
    if eof:
        asyncio.ensure_future(job.service.executeAction('start', context=job.context), loop=loop)


def monitor(job):
    pass
