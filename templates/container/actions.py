
def install(job):
    service = job.service
    node = service.parent
    # Get g8core client
    node = service.parent
    cl = j.clients.g8core.get(host=node.model.data.redisAddr,
                              port=node.model.data.redisPort,
                              password=node.model.data.redisPassword)
    # create ports config
    ports = {}
    if not service.model.data.ports:
        ports = dict(map(int, port.split(':')) for port in service.model.data.ports)

    # create bridges config
    bridges = []
    for bridge in service.model.data.bridges:
        _bridge = service.aysrepo.servicesFind(actor='bridge', name=bridge)[0]
        if str(_bridge.model.data.networkMode) == 'dhcp':
            bridges.append((_bridge.name, str(_bridge.model.data.networkMode)))
        elif str(_bridge.model.data.networkMode) == 'static':
            cidr = _bridge.model.data.setting.to_dict()['cidr']
            bridges.append((_bridge.name, cidr))
        else:
            bridges.append((_bridge.name, ''))

    mount_points = {}
    for fs in service.model.data.filesystems:
        fs_name, container_mount_path = fs.split(':')
        _fs = service.aysrepo.servicesFind(actor='filesystem', name=fs_name)[0]
        mount_points[_fs.model.data.mountpoint] = container_mount_path

    container_id = cl.container.create(root_url=service.model.data.flist,
                                       mount=mount_points,
                                       host_network=service.model.data.hostNetworking or False,
                                       zerotier=service.model.data.zerotier or None,
                                       bridge=bridges,
                                       port=ports,
                                       hostname=service.model.data.hostname or None,
                                       storage=service.model.data.storage or None)
    service.model.data.id = container_id
    service.model.data.status = 'running'


def start(job):
    service = job.service
    node = service.parent
    # Get g8core client
    node = service.parent
    cl = j.clients.g8core.get(host=node.model.data.redisAddr,
                              port=node.model.data.redisPort,
                              password=node.model.data.redisPassword)
    if str(service.model.data.id) not in cl.container.list():
        service.executeAction('install', inprocess=True)


def stop(job):
    service = job.service
    node = service.parent
    # Get g8core client
    node = service.parent
    cl = j.clients.g8core.get(host=node.model.data.redisAddr,
                              port=node.model.data.redisPort,
                              password=node.model.data.redisPassword)
    cl.container.terminate(service.model.data.id)


def monitor(job):
    service = job.service
    service.executeAction('start', inprocess=True)
