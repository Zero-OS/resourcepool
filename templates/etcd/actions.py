from js9 import j


def install(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('start', context=job.context))


def start(job):
    from zeroos.orchestrator.sal.ETCD import ETCD

    service = job.service

    etcd = ETCD.from_ays(service, job.context['token'], logger=service.logger)
    etcd.start()

    service.model.data.status = "running"


def stop(job):
    from zeroos.orchestrator.sal.ETCD import ETCD
    service = job.service
    etcd = ETCD.from_ays(service, job.context['token'], logger=service.logger)
    etcd.stop()


def watchdog_handler(job):
    import asyncio
    service = job.service
    loop = j.atyourservice.server.loop
    etcd_cluster = service.consumers.get('etcd_cluster')
    if etcd_cluster:
        asyncio.ensure_future(etcd_cluster[0].executeAction('watchdog_handler', context=job.context), loop=loop)


def monitor(job):
    from zeroos.orchestrator.configuration import get_jwt_token
    from zeroos.orchestrator.sal.ETCD import ETCD

    service = job.service
    if service.model.actionsState['install'] != 'ok':
        return

    token = get_jwt_token(service.aysrepo)
    etcd = ETCD.from_ays(service, token)
    if service.model.data.status == 'running' and not etcd.is_running():
        job.context['token'] = token
        j.tools.async.wrappers.sync(service.executeAction('start', context=job.context))