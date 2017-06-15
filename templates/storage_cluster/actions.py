from js9 import j


def input(job):
    for arg in ['filesystems', 'arbds']:
        if job.model.args.get(arg, []) != []:
            raise j.exceptions.Input("{} should not be set as input".format(arg))

    nodes = job.model.args.get('nodes', [])
    nrserver = job.model.args.get('nrServer', 0)
    if len(nodes) == 0:
        raise j.exceptions.Input("Invalid amount of nodes provided")
    if nrserver % len(nodes) != 0:
        raise j.exceptions.Input("Invalid spread provided can not evenly spread servers over amount of nodes")

    cluster_type = job.model.args.get("clusterType")

    if cluster_type == "tlog":
        k = job.model.args.get("k", 0)
        m = job.model.args.get("m", 0)
        if not k and not m:
            raise j.exceptions.Input("K and M should be larger than 0")
        if (k + m) > nrserver:
            raise j.exceptions.Input("K and M should be greater than or equal to number of servers")
    return job.model.args


def get_cluster(service):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    return StorageCluster.from_ays(service)


def get_baseport(node):
    ports = node.client.info.port()
    baseport = 2000
    for portInfo in ports:
        port = portInfo.get('port', 0)
        if str(port).startswith('200') and port >= baseport:
            baseport = port + 1
    return baseport


def init(job):
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    from zeroos.orchestrator.sal.Node import Node

    service = job.service
    nodes = []
    for node_service in service.producers['node']:
        nodes.append(Node.from_ays(node_service))
    nodemap = {node.name: node for node in nodes}

    cluster = StorageCluster(service.name, nodes, service.model.data.diskType)
    availabledisks = cluster.find_disks()
    diskpernode = int(service.model.data.nrServer / len(nodes))
    # validate amount of disks and remove unneeded disks
    if service.model.data.nrServer % len(nodes) != 0:
        raise j.exceptions.Input("Amount of servers is not equally devidable by amount of nodes")
    for node, disks in availabledisks.items():
        if len(disks) < diskpernode:
            raise j.exceptions.Input("Not enough available disks on node {}".format(node))
        availabledisks[node] = disks[:diskpernode]
    for node in nodes:
        if node.name not in availabledisks:
            raise j.exceptions.Input("Not enough available disks on node {}".format(node.name))

    # lets create some services
    spactor = service.aysrepo.actorGet("storagepool")
    fsactor = service.aysrepo.actorGet("filesystem")
    containeractor = service.aysrepo.actorGet("container")
    ardbactor = service.aysrepo.actorGet("ardb")
    filesystems = []
    ardbs = []

    def create_server(node, disks, baseport, variant='data'):
        for idx, disk in enumerate(disks):
            baseport += idx
            diskmap = [{'device': disk.devicename}]
            args = {
                'node': node.name,
                'metadataProfile': 'single',
                'dataProfile': 'single',
                'devices': diskmap
            }
            storagepoolname = 'cluster_{}_{}_{}'.format(node.name, service.name, disk.name)
            spactor.serviceCreate(instance=storagepoolname, args=args)
            containername = '{}_{}_{}'.format(storagepoolname, variant, idx)
            # adding filesystem
            args = {
                'storagePool': storagepoolname,
                'name': containername,
            }
            filesystems.append(fsactor.serviceCreate(instance=containername, args=args))
            config = get_configuration(job.service.aysrepo)

            # create containers
            args = {
                'node': node.name,
                'hostname': containername,
                'flist': config.get('rocksdb-flist', 'https://hub.gig.tech/gig-official-apps/ardb-rocksdb.flist'),
                'mounts': [{'filesystem': containername, 'target': '/mnt/data'}],
                'hostNetworking': True
            }
            containeractor.serviceCreate(instance=containername, args=args)
            # create ardbs
            args = {
                'homeDir': '/mnt/data',
                'bind': '{}:{}'.format(node.storageAddr, baseport),
                'container': containername
            }
            ardbs.append(ardbactor.serviceCreate(instance=containername, args=args))
        return baseport

    for nodename, disks in availabledisks.items():
        node = nodemap[nodename]
        # making the storagepools
        baseport = get_baseport(node)
        baseport = create_server(node, disks, baseport) + 1

    if str(service.model.data.clusterType) != 'tlog':
        create_server(node, [disks[-1]], baseport, 'metadata')

    service.model.data.init('filesystems', len(filesystems))
    service.model.data.init('ardbs', len(ardbs))

    for index, fs in enumerate(filesystems):
        service.consume(fs)
        service.model.data.filesystems[index] = fs.name
    for index, ardb in enumerate(ardbs):
        service.consume(ardb)
        service.model.data.ardbs[index] = ardb.name

    job.service.model.data.status = 'empty'


def install(job):
    job.service.model.actions['start'].state = 'ok'
    job.service.model.data.status = 'ready'


def start(job):
    service = job.service

    cluster = get_cluster(service)
    job.logger.info("start cluster {}".format(service.name))
    cluster.start()
    job.service.model.data.status = 'ready'


def stop(job):
    service = job.service
    cluster = get_cluster(service)
    job.logger.info("stop cluster {}".format(service.name))
    cluster.stop()


def delete(job):
    service = job.service
    ardbs = service.producers.get('ardb', [])
    filesystems = service.producers.get('filesystem', [])

    for ardb in ardbs:
        container = ardb.parent
        j.tools.async.wrappers.sync(container.executeAction('stop'))
        j.tools.async.wrappers.sync(container.delete())

    for fs in filesystems:
        if not fs.parent:
            continue
        pool = fs.parent
        j.tools.async.wrappers.sync(pool.executeAction('delete'))
        j.tools.async.wrappers.sync(pool.delete())

    job.logger.info("stop cluster {}".format(service.name))
    job.service.model.data.status = 'empty'


def addStorageServer(job):
    raise NotImplementedError()


def reoveStorageServer(job):
    raise NotImplementedError()
