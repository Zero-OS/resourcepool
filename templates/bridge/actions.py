
def install(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    job.context['token'] = get_jwt_token(service.aysrepo)

    # Get g8core client
    node = Node.from_ays(service.parent, job.context['token'])

    # Create bridge
    network = None if str(service.model.data.networkMode) == "none" else str(service.model.data.networkMode)

    try:
        node.client.bridge.create(service.name,
                                  hwaddr=service.model.data.hwaddr or None,
                                  network=network,
                                  nat=service.model.data.nat,
                                  settings=service.model.data.setting.to_dict())
    except RuntimeError as e:
        service.model.data.status = 'error'
        raise e

    service.model.data.status = 'up'


def delete(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    job.context['token'] = get_jwt_token(service.aysrepo)

    # Get node client
    node = Node.from_ays(service.parent, job.context['token'])

    if service.model.data.status == 'error':
        if service.name not in node.client.bridge.list():
            return

    node.client.bridge.delete(service.name)
    service.model.data.status = 'down'


def monitor(job):
    import asyncio
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    if service.parent.model.data.status != 'running':
        return

    # Get node client
    token = get_jwt_token(job.service.aysrepo)
    node = Node.from_ays(service.parent, token)

    if service.model.data.status != 'up' or service.name in node.client.bridge.list():
        return

    job.context['token'] = token
    asyncio.ensure_future(service.executeAction('install', context=job.context), loop=service._loop)
