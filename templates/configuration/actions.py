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
    import requests

    configurations = {conf['key']: conf['value'] for conf in configs}
    js_version = configurations.get('js-version')
    jwt_token = configurations.get('jwt-token')
    jwt_key = configurations.get('jwt-key')

    rc, out, err = j.sal.process.execute('git symbolic-ref -q --short HEAD || git describe --tags --exact-match', cwd='/opt/code/github/jumpscale/core9')
    if rc != 0:
        raise j.exceptions.RuntimeError("Can't read version of jumpscale: %s" % err)
    installed_version = out.strip()

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

    # validate 0-stor configurations
    zstor_organization = configurations.get("0-stor-organization")
    zstor_namespace = configurations.get("0-stor-namespace")
    zstor_clientid = configurations.get("0-stor-clientid")
    zstor_clientsecret = configurations.get("0-stor-clientsecret")
    if not (zstor_organization and zstor_namespace and zstor_clientid and zstor_clientsecret):
        return

    # The conactenation here because ays parsing can't handle the string in one line
    # original commit 0bdf5f5f2bb7bf266ac37a148096e5af1342784b

    url = "https://itsyou.online/v1/oauth/access_token"
    scope = "user:memberof:{org}.0stor.{namespace}.read,user:memberof:{org}.0stor.{namespace}.write,user:memberof:{org}.0stor.{namespace}.delete"
    scope = scope.format(
        org=zstor_organization,
        namespace=zstor_namespace
    )
    params = {
        "client_id": zstor_clientid,
        "client_secret": zstor_clientsecret,
        "grant_type": "client_credentials",
        "response_type": "id_token",
        "scope": scope,
    }
    res = requests.post(url, params=params)
    if res.status_code != 200:
        raise RuntimeError("Invalid itsyouonline configuration")


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
