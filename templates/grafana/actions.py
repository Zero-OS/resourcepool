from js9 import j


def get_container(service, force=True):
    containers = service.producers.get('container')
    if not containers:
        if force:
            raise RuntimeError('Service didn\'t consume any containers')
        else:
            return
    return containers[0]


def add_datasources(grafana, influxes):
    for influx in influxes:
        for i, database in enumerate(influx.model.data.databases):
            grafana.add_data_source(database, influx.name, influx.parent.model.data.redisAddr, influx.model.data.port, i)


def delete_datasources(grafana, influxes):
    for influx in influxes:
        for i, database in enumerate(influx.model.data.databases):
            grafana.delete_data_source(influx.name)


def init(job):
    from zeroos.orchestrator.configuration import get_configuration

    service = job.service
    container_actor = service.aysrepo.actorGet('container')
    config = get_configuration(service.aysrepo)

    args = {
        'node': service.model.data.node,
        'flist': config.get(
            '0-grafana-flist', 'https://hub.gig.tech/gig-official-apps/grafana.flist'),
        'hostNetworking': True
    }
    cont_service = container_actor.serviceCreate(instance='{}_grafana'.format(service.name), args=args)
    service.consume(cont_service)


def install(job):
    start(job)


def start(job):
    from zeroos.orchestrator.sal.grafana.grafana import Grafana
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    service.model.data.status = 'running'
    container = get_container(service)
    container.executeAction('start', context=job.context)
    container_ays = Container.from_ays(container, job.context['token'], logger=service.logger)
    grafana = Grafana(container_ays, service.parent.model.data.redisAddr, job.service.model.data.port, job.service.model.data.url)
    grafana.start()
    add_datasources(grafana, service.producers.get('influxdb'))
    service.saveAll()


def stop(job):
    from zeroos.orchestrator.sal.grafana.grafana import Grafana
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    container = get_container(service)
    container_ays = Container.from_ays(container, job.context['token'], logger=service.logger)
    if container_ays.is_running():
        grafana = Grafana(container_ays, service.parent.model.data.redisAddr, job.service.model.data.port, job.service.model.data.url)
        grafana.stop()
        container.executeAction('stop', context=job.context)

    service.model.data.status = 'halted'
    service.saveAll()


def uninstall(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    container = get_container(service, False)

    if container:
        stop(job)
        container.delete()
    service.delete()


def processChange(job):
    from zeroos.orchestrator.sal.grafana.grafana import Grafana
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    args = job.model.args

    if args.pop('changeCategory') != 'dataschema' or service.model.actionsState['install'] in ['new', 'scheduled']:
        return
    container = get_container(service)
    container_ays = Container.from_ays(container, job.context['token'], logger=service.logger)
    grafana = Grafana(container_ays, service.parent.model.data.redisAddr, job.service.model.data.port, job.service.model.data.url)

    if 'url' in args:
        service.model.data.url = args.get('url', service.model.data.url)
        if container_ays.is_running() and grafana.is_running()[0]:
            grafana.stop()
            grafana.url = service.model.data.url
            grafana.start()

    service.saveAll()


def init_actions_(service, args):
    return {
        'init': [],
        'install': ['init'],
        'monitor': ['start'],
        'delete': ['uninstall'],
        'uninstall': [],
    }


def monitor(job):
    pass

