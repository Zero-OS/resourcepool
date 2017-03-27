
def install(job):
    import g8core
    service = job.service

    # Get g8core client
    node = service.parent
    cl = g8core.Client(host=node.model.data.redisAddr,
                       port=node.model.data.redisPort,
                       password=node.model.data.redisPassword,
                       db=0,
                       timeout=None)

    # Create bridge
    network_map = {
        0: None,
        1: 'static',
        2: 'dnsmasq',
    }
    cl.bridge.create(service.model.data.name,
                     hwaddr=service.model.data.hwaddr or None,
                     network=network_map[service.model.data.networkMode.raw],
                     nat=service.model.data.nat,
                     settings=service.model.data.setting.to_dict())
    service.model.data.status = 'up'


def delete(job):
    import g8core
    service = job.service

    # Get g8core client
    node = service.parent
    cl = g8core.Client(host=node.model.data.redisAddr,
                       port=node.model.data.redisPort,
                       password=node.model.data.redisPassword,
                       db=0,
                       timeout=None)
    cl.bridge.delete(service.model.data.name)
    service.model.data.status = 'down'
