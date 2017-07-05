from js9 import j


def input(job):
    ays_repo = job.service.aysrepo
    services = ays_repo.servicesFind(actor=job.service.model.dbobj.actorName)

    if services and job.service.name != services[0].name:
        raise j.exceptions.RuntimeError('Repo can\'t contain multiple statsdb services')


def init(job):
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    influxdb_actor = service.aysrepo.actorGet('influxdb')

    args = {
        'node': service.model.data.node,
        'port': service.model.data.port,
        'databases': ['statistics']
    }
    influxdb_service = influxdb_actor.serviceCreate(instance=service.name, args=args)
    service.consume(influxdb_service)


def get_influxdb(job):
    influxdbs = job.service.producers.get('influxdb')
    if not influxdbs:
        raise RuntimeError('Service didn\'t consume any influxdbs')
    return influxdbs[0]


def install(job):
    j.tools.async.wrappers.sync(job.service.executeAction('start', context=job.context))


def start(job):
    influxdb = get_influxdb(job)
    j.tools.async.wrappers.sync(influxdb.executeAction('start', context=job.context))
    job.service.model.data.status = 'running'
    job.service.saveAll()


def stop(job):
    influxdb = get_influxdb(job)
    j.tools.async.wrappers.sync(influxdb.executeAction('stop', context=job.context))
    job.service.model.data.status = 'halted'
    job.service.saveAll()


def uninstall(job):
    influxdb = get_influxdb(job)
    j.tools.async.wrappers.sync(influxdb.executeAction('uninstall', context=job.context))
    job.service.delete()


def processChange(job):
    service = job.service
    args = job.model.args
    if args.pop('changeCategory') != 'dataschema' or service.model.actionsState['install'] in ['new', 'scheduled']:
        return

    if args.get('port'):
        influxdb = get_influxdb(job)
        service.model.data.port = args['port']
        pc_job = influxdb.getJob('processChange')
        pc_job.model.args = {'port': args.get('port')}
        pc_job.executeInProcess()
        influxdb = get_influxdb(job)
        job.service.model.data.status = influxdb.model.data.status

    service.saveAll()


