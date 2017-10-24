from js9 import j


def install(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    service.executeAction('start', context=job.context)


def start(job):
    from zeroos.orchestrator.sal.ETCD import ETCD
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service

    etcd = ETCD.from_ays(service, job.context['token'], logger=service.logger)
    etcd.start()

    service.model.data.status = "running"


def stop(job):
    from zeroos.orchestrator.sal.ETCD import ETCD
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    etcd = ETCD.from_ays(service, job.context['token'], logger=service.logger)
    etcd.stop()


def watchdog_handler(job):
    import asyncio
    service = job.service
    etcd_cluster = service.consumers.get('etcd_cluster')
    if etcd_cluster:
        etcd_cluster[0].self_heal_action('watchdog_handler')


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
        service.executeAction("start", context=job.context)
