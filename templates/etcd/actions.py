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

def stop(job):
    from zeroos.orchestrator.sal.ETCD import ETCD
    service = job.service
    etcd = ETCD.from_ays(service, job.context['token'])
    etcd.stop()


def watchdog_handler(job):
    import asyncio
    service = job.service
    loop = j.atyourservice.server.loop
    etcd_cluster = service.consumers.get('etcd_cluster')
    if etcd_cluster:
        asyncio.ensure_future(etcd_cluster[0].executeAction('watchdog_handler', context=job.context), loop=loop)
