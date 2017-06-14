def get_configuration_and_service(ays_repo):
    services = ays_repo.servicesFind(actor='configuration')
    if len(services) > 1:
        raise RuntimeError('Multiple configuration services found')

    service = services[0] if services else None
    configuration = service.model.data.to_dict()['configurations'] if service else []

    return {conf['key']: conf['value'] for conf in configuration}, service


def get_configuration(ays_repo):
    configs, _ = get_configuration_and_service(ays_repo)
    return configs


def get_jwt_token(ays_repo):
    from jose import jwt
    import time
    import requests

    configs, service = get_configuration_and_service(ays_repo)
    jwt_token = configs.get('jwt-token')
    jwt_key = configs.get('jwt-key')
    if not jwt_token:
        return None

    try:
        token = jwt.decode(jwt_token, jwt_key)
    except Exception:
        raise RuntimeError('Invalid jwt-token and jwt-key combination')

    if token['exp'] > time.time():
        headers = {'Authorization': 'bearer %s' % jwt_token}
        resp = requests.get('https://itsyou.online/v1/oauth/jwt/refresh', headers=headers)
        jwt_token = resp.content.decode()

        for config in service.model.data.configurations:
            if config.key == 'jwt-token':
                config.value = jwt_token
                break

        service.saveAll()

    return jwt_token
