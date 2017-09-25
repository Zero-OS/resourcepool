def install(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token
    service = job.service

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    node = Node.from_ays(service.parent, job.context['token'])
    if node.client.nft.rule_exists(service.model.data.port):
        return
    node.client.nft.open_port(service.model.data.port)
    service.model.data.status = "opened"
    service.saveAll()


def drop(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token
    service = job.service

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    node = Node.from_ays(service.parent, job.context['token'])
    if not node.client.nft.rule_exists(service.model.data.port):
        return
    node.client.nft.drop_port(service.model.data.port)
    service.model.data.status = "dropped"
    service.saveAll()
