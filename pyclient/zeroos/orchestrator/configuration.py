def get_configuration(ays_repo):
    services = ays_repo.servicesFind(actor='configuration')
    if len(services) > 1:
        raise RuntimeError('Multiple configuration services found')

    configuration = services[0].model.data.to_dict()['configurations'] if services else []
    return {conf['key']: conf['value'] for conf in configuration}
