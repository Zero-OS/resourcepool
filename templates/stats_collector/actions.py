def get_init_processes(service):
    from zeroos.orchestrator.configuration import get_jwt_token

    token = get_jwt_token(service.aysrepo)
    cmd_args = []

    if token:
        cmd_args.extend(['-- token', token])
    if service.model.data.ip:
        cmd_args.extend(['--ip', service.model.data.ip])
    if service.model.data.port:
        cmd_args.extend(['--port', str(service.model.data.port)])
    if service.model.data.db:
        cmd_args.extend(['--db', service.model.data.db])
    if service.model.data.retention:
        cmd_args.extend(['--retention', service.model.data.retention])

    return [
        {
            'name': '0-statscollector',
            'args': cmd_args
        }
    ]


def init(job):
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    container_actor = service.aysrepo.actorGet('container')
    config = get_configuration(service.aysrepo)
    parent = service.parent.model.data

    args = {
        'node': service.model.data.node,
        'flist': config.get(
            '0-statscollector-flist', 'https://hub.gig.tech/gig-official-apps/0-statscollector-master.flist'),
        'hostNetworking': True,
        'initProcesses': get_init_processes(service)
    }
    cont_service = container_actor.serviceCreate(instance=service.name, args=args)
    service.consume(cont_service)


def install(job):
    service = job.service
    containers = service.producers.get('container')
    if containers:
        j.tools.async.wrappers.sync(containers[0].executeAction('start', context=job.context))
    service.model.data.status = 'running'
    service.saveAll()


def uninstall(job):
    service = job.service
    containers = service.producers.get('container')
    if containers:
        j.tools.async.wrappers.sync(containers[0].executeAction('stop', context=job.context))
        j.tools.async.wrappers.sync(containers[0].delete())
    service.delete()


def processChange(job):
    from zeroos.orchestrator.configuration import get_jwt_token_from_job
    service = job.service
    args = job.model.args

    if args.pop('changeCategory') != 'dataschema' or service.model.actionsState['install'] in ['new', 'schedules']:
        return

    if args.get('ip'):
        service.model.data.ip = args['ip']
    if args.get('port'):
        service.model.data.port = args['port']
    if args.get('db'):
        service.model.data.db = args['db']
    if args.get('retention'):
        service.model.data.retention = args['retention']

    containers = service.producers.get('container')
    if containers:
        container = containers[0]
        container.model.data.initProcesses = get_init_processes(service)
        container.saveAll()

        job.context['token'] = get_jwt_token_from_job(job)
        j.tools.async.wrappers.sync(container.executeAction('stop', context=job.context))
        service.model.data.status = 'halted'
        j.tools.async.wrappers.sync(container.executeAction('start', context=job.context))
        service.model.data.status = 'running'

    service.saveAll()


def init_actions_(service, args):
    return {
        'init': [],
        'install': ['init'],
        'monitor': ['start'],
        'delete': ['uninstall'],
        'uninstall': [],
    }
