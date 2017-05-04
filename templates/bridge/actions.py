
def install(job):
    service = job.service

    # Get g8core client
    node = service.parent
    cl = j.clients.g8core.get(host=node.model.data.redisAddr,
                              port=node.model.data.redisPort,
                              password=node.model.data.redisPassword)

    # Create bridge
    network = None if str(service.model.data.networkMode) == "none" else str(service.model.data.networkMode)
    cl.bridge.create(service.name,
                     hwaddr=service.model.data.hwaddr or None,
                     network=network,
                     nat=service.model.data.nat,
                     settings=service.model.data.setting.to_dict())
    service.model.data.status = 'up'


def delete(job):
    service = job.service

    # Get g8core client
    node = service.parent
    cl = j.clients.g8core.get(host=node.model.data.redisAddr,
                              port=node.model.data.redisPort,
                              password=node.model.data.redisPassword)
    cl.bridge.delete(service.name)
    service.model.data.status = 'down'
