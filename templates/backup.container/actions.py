from js9 import j


def install(job):
    from zeroos.orchestrator.sal.Container import Container

    service = job.service
    container_service = service.aysrepo.serviceGet(role='container', instance=service.model.data.container)
    container = Container.from_ays(container_service, job.context['token'])

    id = container.id
    client = container.node.client
    r = client.container.backup(id, service.model.data.url)

    service.model.data.type = 'container'

    meta = {
        'name': container.name,
        'node': container.node.addr,
        'nics': container.nics,
        'hostname': container.hostname,
        'flist': container.flist,
        'ports': container.ports,
        'host_network': container.host_network,
        'storage': container.storage,
        'init_processes': container.init_processes,
        'privileged': container.privileged,
    }

    service.model.data.meta = j.data.serializer.json.dumps(meta)
    service.model.data.snapshot = r.get()
    service.saveAll()


def monitor(job):
    pass
