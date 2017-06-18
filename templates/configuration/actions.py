from js9 import j


def input(job):
    ays_repo = job.service.aysrepo
    services = ays_repo.servicesFind(actor=job.service.model.dbobj.actorName)

    if services and job.service.name != services[0].name:
        raise j.exceptions.RuntimeError('Repo can\'t contain multiple configuration services')

    configs = job.model.args.get('configurations', [])
    validate_configs(configs)


def validate_configs(configs):
    import jose

    configurations = {conf['key']: conf['value'] for conf in configs}
    js_version = configurations.get('js-version')
    jwt_token = configurations.get('jwt-token')
    jwt_key = configurations.get('jwt-key')

    installed_version = j.core.state.versions.get('JumpScale9')
    if js_version and not js_version.startswith('v') and installed_version.startswith('v'):
        installed_version = installed_version[1:]
    if js_version and not installed_version.startswith(js_version):
        raise j.exceptions.Input('Required jumpscale version is %s but installed version is %s.' % (js_version, installed_version))

    if jwt_token:
        if not jwt_key:
            raise j.exceptions.Input('JWT key is not configured')
        try:
            jose.jwt.decode(jwt_token, jwt_key)
        except jose.exceptions.ExpiredSignatureError:
            pass
        except Exception:
            raise j.exceptions.Input('Invalid jwt-token and jwt-key combination')


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
