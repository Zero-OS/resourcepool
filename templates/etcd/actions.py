from js9 import j


def install(job):
    from zeroos.orchestrator.sal.ETCD import ETCD

    service = job.service

    etcd = ETCD.from_ays(service, job.context['token'])
    etcd.start()

    service.model.data.status = "running"


def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install', context=job.context))


def watchdog_handler(job):
    import asyncio
    service = job.service
    loop = j.atyourservice.server.loop
    if service.model.data.status == 'running':
        asyncio.ensure_future(job.service.executeAction('start', context=job.context), loop=loop)
