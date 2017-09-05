
def install(job):
    from zeroos.orchestrator.sal.Container import Container

    service = job.service
    container_service = service.aysrepo.serviceGet(role='container', instance=service.model.data.container)
    container = Container.from_ays(container_service, job.context['token'])

    id = container.id
    client = container.node.client
    r = client.container.backup(id, service.model.data.url)

    service.model.data.snapshot = r.get()
    service.saveAll()
