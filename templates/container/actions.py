def input(job):
    # make sure we always consume all the filesystems used in the mounts property
    args = job.model.args
    mounts = args.get('mounts', [])
    if 'filesystems' not in args:
        args['filesystems'] = []
    filesystems = args['filesystems']
    for mount_point in mounts:
        fs_name, _ = mount_point.split(':')
        if fs_name not in filesystems:
            args['filesystems'].append(fs_name)

    return args


def install(job):
    service = job.service
    # Get g8core client
    cl = service.actions.get_node_client_(service)

    # create ports config
    ports = {}
    if len(service.model.data.ports) > 0:
        ports = dict(map(int, port.split(':')) for port in service.model.data.ports)

    # create bridges config
    bridges = []
    for _bridge in service.producers.get('bridge', []):
        if str(_bridge.model.data.networkMode) == 'dnsmasq':
            bridges.append((_bridge.name, 'dhcp'))
        elif str(_bridge.model.data.networkMode) == 'static':
            cidr = _bridge.model.data.setting.to_dict()['cidr']
            bridges.append((_bridge.name, cidr))
        else:
            bridges.append((_bridge.name, ''))

    # Create mount points mapping
    mount_points = {}
    for mount_point in service.model.data.mounts:
        fs_name, container_mount_path = mount_point.split(':')
        _fs = service.aysrepo.serviceGet(role='filesystem', instance=fs_name)
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
    if str(service.model.data.status) == "halted":
        coro = service.executeAction('install')
        j.tools.async.wrappers.sync(coro)


def stop(job):
    service = job.service
    if str(service.model.data.status) == "running":
        # Get g8core client
        cl = service.actions.get_node_client_(service)
        cl.container.terminate(service.model.data.id)
        service.model.data.status = 'halted'


def monitor(job):
    service = job.service
    # Get g8core client
    cl = service.actions.get_node_client_(service)
    if str(service.model.data.id) not in cl.container.list():
        coro = service.executeAction('start')
        j.tools.async.wrappers.sync(coro)


def get_node_client_(service):
    node = service.parent
    return j.clients.g8core.get(host=node.model.data.redisAddr,
                                port=node.model.data.redisPort,
                                password=node.model.data.redisPassword)


def get_container_client_(service):
    if str(service.model.data.status) == "running":
        # Get g8core client
        cl = service.actions.get_node_client_(service)
        return cl.container.client(service.model.data.id)
