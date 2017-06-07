from js9 import j


def input(job):
    ays_repo = job.service.aysrepo
    services = ays_repo.servicesFind(actor=job.service.model.dbobj.actorName)

    if services and job.service.name != services[0].name:
        raise j.exceptions.RuntimeError('Repo can\'t contain multiple configuration services')

    configs = job.model.args.get('configurations', [])
    validate_configs(configs)


def validate_configs(configs):
    js_version = None
    for config in configs:
        if config.get('key') == 'js-version':
            js_version = config.get('value')
            break

    installed_version = j.core.state.versions.get('JumpScale9')
    if js_version and not js_version.startswith('v') and installed_version.startswith('v'):
        installed_version = installed_version[1:]
    if js_version and js_version != installed_version:
        raise j.exceptions.RuntimeError('Required jumpscale version is %s but installed version is %s.' % (js_version, installed_version))


def processChange(job):
    service = job.service
    args = job.model.args
    category = args.pop('changeCategory')
    if category == 'dataschema':
        configs = args.get('configurations')
        if configs:
            validate_configs(configs)
            service.model.data.configurations = args.get('configurations', service.model.data.configurations)
            service.saveAll()
