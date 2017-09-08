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

    if cluster_type == "object":
        data_shards = job.model.args.get("dataShards", 0)
        parity_shards = job.model.args.get("parityShards", 0)
        if not data_shards or not parity_shards:
            raise j.exceptions.Input("dataShards and parityShards should be larger than 0")
        if (data_shards + parity_shards) > nrserver:
            raise j.exceptions.Input("dataShards and parityShards should be greater than or equal to number of servers")
    return job.model.args


def get_cluster(job):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    return StorageCluster.from_ays(job.service, job.context['token'])


def get_disks(job, nodes):
    """
    Get disks to be used by StorageEngine, 0-stor
    It takes into account that StorageEngine, 0-stor data, 0-stor meta disks can be of different types
    """
    service = job.service

    disktypes = []
    diskType = service.model.data.diskType
    disktypes.append(diskType)

    if service.model.data.clusterType == "object":
        metadiskType = service.model.data.metadiskType
        disktypes.append(metadiskType)

    diskmap = {}
    # Get disks of different types and add it to diskmap
    # diskmap example: {hdd: {node: [vda, vdb, vdc]}}
    for disktype in set(disktypes):
        if disktype not in diskmap:
            diskmap[disktype] = get_availabledisks(job, nodes, disktype=disktype)

        disknumber = 0
        for node, disks in diskmap[disktype].items():
            if node == "":
                continue
            disknumber += len(disks)
        diskmap[disktype]["disknumber"] = disknumber

    # validate amount of disks and removdiskpernodee unneeded disks
    serverpernode = service.model.data.nrServer // len(nodes)
    if service.model.data.nrServer % len(nodes) != 0:
        raise j.exceptions.Input("Amount of servers is not equally devidable by amount of nodes")

    datadisks = {}
    metadisks = {}
    for key, value in diskmap.items():
        disklen = value.pop("disknumber")
        diskpernode = (disktypes.count(key) * service.model.data.nrServer) // len(nodes)
        if disklen == 0:
            raise j.exceptions.Input("No available disks of type {} found".format(key))

        for node, disks in value.items():
            if len(disks) < diskpernode:
                raise j.exceptions.Input("Not enough available disks on node {}".format(node))

            # populate datadisks, metadisks based on their disk type
            if key == diskType:
                datadisks[node] = disks[:serverpernode]

            if service.model.data.clusterType == "object":
                disks = disks[serverpernode:]
                if key == metadiskType:
                    metadisks[node] = disks[:serverpernode]

    return datadisks, metadisks


def init(job):
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.sal.Node import Node

    service = job.service
    nodes = set()
    for node_service in service.producers['node']:
        nodes.add(Node.from_ays(node_service, job.context['token']))
    nodes = list(nodes)
    nodemap = {node.name: node for node in nodes}

    datadisks, metadisks = get_disks(job, nodes)

    # lets create some services
    spactor = service.aysrepo.actorGet("storagepool")
    fsactor = service.aysrepo.actorGet("filesystem")
    containeractor = service.aysrepo.actorGet("container")
    storageEngineActor = service.aysrepo.actorGet("storage_engine")
    zerostorActor = service.aysrepo.actorGet("zerostor")

    filesystems = []
    storageEngines = []

    def create_server(node, disk, baseport, tcp, variant='data', metadisk=None):
        diskmap = [{'device': disk.devicename}]
        args = {
            'node': node.name,
            'metadataProfile': 'single',
            'dataProfile': 'single',
            'devices': diskmap
        }
        storagepoolname = 'cluster_{}_{}_{}'.format(node.name, service.name, disk.name)
        spservice = spactor.serviceCreate(instance=storagepoolname, args=args)
        service.consume(spservice)

        containername = '{}_{}_{}'.format(storagepoolname, variant, baseport)
        # adding filesystem
        args = {
            'storagePool': storagepoolname,
            'name': containername,
        }
        filesystems.append(fsactor.serviceCreate(instance=containername, args=args))
        config = get_configuration(job.service.aysrepo)

        if service.model.data.clusterType == "object":
            diskmap = [{'device': metadisk.devicename}]
            args = {
                'node': node.name,
                'metadataProfile': 'single',
                'dataProfile': 'single',
                'devices': diskmap
            }
            metastoragepoolname = 'cluster_{}_{}_{}'.format(node.name, service.name, metadisk.name)
            metaspservice = spactor.serviceCreate(instance=metastoragepoolname, args=args)
            service.consume(metaspservice)

            metacontainername = '{}_{}_{}_meta'.format(metastoragepoolname, variant, baseport)
            # adding filesystem
            args = {
                'storagePool': metastoragepoolname,
                'name': metacontainername,
            }
            filesystems.append(fsactor.serviceCreate(instance=metacontainername, args=args))

            # create containers
            args = {
                'node': node.name,
                'hostname': metacontainername,
                'flist': config.get('0-stor-flist', 'https://hub.gig.tech/gig-official-apps/0-stor-master.flist'),
                'mounts': [{'filesystem': containername, 'target': '/mnt/data'}, {'filesystem': metacontainername, 'target': '/mnt/metadata'}],
                'hostNetworking': True
            }
            containeractor.serviceCreate(instance=containername, args=args)

            # create zerostor
            args = {
                'dataDir': '/mnt/data',
                'metaDir': '/mnt/metadata',
                'bind': '{}:{}'.format(node.storageAddr, baseport),
                'container': containername
            }
            zerostorService = zerostorActor.serviceCreate(instance=containername, args=args)
            zerostorService.consume(tcp)
            service.consume(zerostorService)
            return

        # create containers
        args = {
            'node': node.name,
            'hostname': containername,
            'flist': config.get('storage-engine-flist', 'https://hub.gig.tech/gig-official-apps/ardb-rocksdb.flist'),
            'mounts': [{'filesystem': containername, 'target': '/mnt/data'}],
            'hostNetworking': True
        }
        containeractor.serviceCreate(instance=containername, args=args)
        # create storageEngines
        args = {
            'homeDir': '/mnt/data',
            'bind': '{}:{}'.format(node.storageAddr, baseport),
            'container': containername
        }
        storageEngine = storageEngineActor.serviceCreate(instance=containername, args=args)
        storageEngine.consume(tcp)
        storageEngines.append(storageEngine)
    for nodename, disks in datadisks.items():
        node = nodemap[nodename]
        # making the storagepool
        nrports = len(disks) + 1 if service.model.data.clusterType == "block" else len(disks)
        baseports, tcpservices = get_baseports(job, node, baseport=2000, nrports=nrports)
        for idx, disk in enumerate(disks):
            if service.model.data.clusterType == "object":
                metadisk = metadisks[nodename][idx]
                create_server(node, disk, baseports[idx], tcpservices[idx], variant="stor", metadisk=metadisk)
                continue
            create_server(node, disk, baseports[idx], tcpservices[idx])

    if service.model.data.clusterType == "block":
        create_server(node, disk, baseports[-1], tcpservices[-1], variant='metadata')

    service.model.data.init('filesystems', len(filesystems))
    service.model.data.init('storageEngines', len(storageEngines))

    for index, fs in enumerate(filesystems):
        service.consume(fs)
        service.model.data.filesystems[index] = fs.name
    for index, storageEngine in enumerate(storageEngines):
        service.consume(storageEngine)
        service.model.data.storageEngines[index] = storageEngine.name

    grafanasrv = service.aysrepo.serviceGet(role='grafana', instance='statsdb', die=False)
    if grafanasrv:
        import json
        from zeroos.orchestrator.sal.StorageCluster import StorageDashboard
        board = StorageDashboard(service).dashboard_template()
        board = json.dumps(board)
        dashboard_actor = service.aysrepo.actorGet('dashboard')
        args = {
            'grafana': 'statsdb',
            'dashboard': board
        }
        dashboardsrv = dashboard_actor.serviceCreate(instance=service.name, args=args)
        service.consume(dashboardsrv)
    job.service.model.data.status = 'empty'


def save_config(job):
    import yaml
    import requests
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    from zeroos.core0.client import Client
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_configuration
    aysconfig = get_configuration(job.service.aysrepo)

    service = job.service
    etcd_cluster = service.producers['etcd_cluster'][0]
    etcd = EtcdCluster.from_ays(etcd_cluster, job.context['token'])

    if service.model.data.clusterType == "block":
        try:
            cluster = StorageCluster.from_ays(service, job.context['token'])
        except ConnectionError as e:
            if e.args:
                job.logger.error(e.args[0])
            else:
                job.logger.error('could connect to storage cluster %s' % service.name)
            return
        config = cluster.get_config()

        yamlconfig = yaml.safe_dump(config, default_flow_style=False)

        etcd.put(key="%s:cluster:conf:storage" % service.name, value=yamlconfig)
        return

    # Push zerostorconfig to etcd
    zerostor_services = service.producers["zerostor"]
    0-stor-organization = aysconfig["0-stor-organization"]
    0-stor-namespace = aysconfig["0-stor-namespace"]
    iyo_client_id = aysconfig["0-stor-clientid"]
    0-stor-clientsecret = aysconfig["0-stor-clientsecret"]

    # The conactenation here because ays parsing can't handle the string in one line
    url = "https://itsyou.online/v1/oauth/access_token"
    scope = "user:memberof:{org}.0stor.{namespace}.read,user:memberof:{org}.0stor.{namespace}.write,user:memberof:{org}.0stor.{namespace}.delete"
    scope = scope.format(
        org=0-stor-organization,
        namespace=0-stor-namespace
    )
    params = {
        "client_id": iyo_client_id,
        "client_secret": 0-stor-clientsecret,
        "grant_type": "client_credentials",
        "response_type": "id_token",
        "scope": scope,
    }
    res = requests.post(url, params=params)
    if res.status_code != 200:
        raise RuntimeError("Invalid itsyouonline configuration")

    zerostor_config = {
        "iyo": {
            "org": 0-stor-organization,
            "namespace": 0-stor-namespace,
            "clientID": iyo_client_id,
            "secret": 0-stor-clientsecret,
        },
        "servers": [{"address": zservice.model.data.bind} for zservice in zerostor_services],
        "metadataServers": [{"address": dialstring} for dialstring in etcd.dialstrings.split(",")],
    }
    yamlconfig = yaml.safe_dump(zerostor_config, default_flow_style=False)
    etcd.put(key="%s:cluster:conf:zerostor" % service.name, value=yamlconfig)


def get_availabledisks(job, nodes, disktype=None):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster

    service = job.service

    disk_type = service.model.data.diskType if disktype is None else disktype

    used_disks = {}
    for node in nodes:
        disks = set()
        pools = service.aysrepo.servicesFind(role='storagepool', parent='node.zero-os!%s' % node.name)
        for pool in pools:
            devices = {device.device for device in pool.model.data.devices}
            disks.update(devices)
        used_disks[node.name] = disks

    cluster = StorageCluster(service.name, nodes, disk_type)
    availabledisks = cluster.find_disks()
    freedisks = {}
    for node, disks in availabledisks.items():
        node_disks = []
        for disk in disks:
            if disk.devicename not in used_disks[node]:
                node_disks.append(disk)
        freedisks[node] = node_disks
    return freedisks


def get_baseports(job, node, baseport, nrports):
    service = job.service
    tcps = service.aysrepo.servicesFind(role='tcp', parent='node.zero-os!%s' % node.name)

    usedports = set()
    for tcp in tcps:
        usedports.add(tcp.model.data.port)

    freeports = []
    tcpactor = service.aysrepo.actorGet("tcp")
    tcpservices = []
    while True:
        if baseport not in usedports:
            baseport = node.freeports(baseport=baseport, nrports=1)[0]
            args = {
                'node': node.name,
                'port': baseport,
            }
            tcp = 'tcp_{}_{}'.format(node.name, baseport)
            tcpservices.append(tcpactor.serviceCreate(instance=tcp, args=args))
            freeports.append(baseport)
            if len(freeports) >= nrports:
                return freeports, tcpservices
        baseport += 1


def install(job):
    dashboardsrv = job.service.aysrepo.serviceGet(role='dashboard', instance=job.service.name, die=False)
    if dashboardsrv:
        cluster = get_cluster(job)
        dashboardsrv.model.data.dashboard = cluster.dashboard
        j.tools.async.wrappers.sync(dashboardsrv.executeAction('install', context=job.context))

    save_config(job)
    job.service.model.actions['start'].state = 'ok'
    job.service.model.data.status = 'ready'
    job.service.saveAll()


def start(job):
    service = job.service

    cluster = get_cluster(job)
    job.logger.info("start cluster {}".format(service.name))
    cluster.start()
    job.service.model.data.status = 'ready'


def stop(job):
    service = job.service
    cluster = get_cluster(job)
    job.logger.info("stop cluster {}".format(service.name))
    cluster.stop()


def delete(job):
    service = job.service
    storageEngines = service.producers.get('storage_engine', [])
    pools = service.producers.get('storagepool', [])

    for storageEngine in storageEngines:
        tcps = storageEngine.producers.get('tcp', [])
        for tcp in tcps:
            j.tools.async.wrappers.sync(tcp.executeAction('drop', context=job.context))
            j.tools.async.wrappers.sync(tcp.delete())

        container = storageEngine.parent
        j.tools.async.wrappers.sync(container.executeAction('stop', context=job.context))
        j.tools.async.wrappers.sync(container.delete())

    for pool in pools:
        j.tools.async.wrappers.sync(pool.executeAction('delete', context=job.context))
        j.tools.async.wrappers.sync(pool.delete())

    job.logger.info("stop cluster {}".format(service.name))
    job.service.model.data.status = 'empty'


def list_vdisks(job):
    import random
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.ETCD import EtcdCluster

    service = job.service

    nodes = [node for node in service.producers['node'] if node.model.data.status != "halted"]
    node = random.choice(nodes)

    # create temp container of 0-disk
    container_name = 'vdisk_list_{}'.format(service.name)
    node = Node.from_ays(node, job.context['token'])
    config = get_configuration(job.service.aysrepo)

    container = Container(name=container_name,
                          flist=config.get('0-disk-flist', 'https://hub.gig.tech/gig-official-apps/0-disk-master.flist'),
                          host_network=True,
                          node=node)
    container.start()
    try:
        cluster = StorageCluster.from_ays(service, job.context['token'])
        clusterconfig = cluster.get_config()

        etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
        etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context['token'])
        cmd = '/bin/zeroctl list vdisks {}'.format(clusterconfig['metadataStorage']["address"])
        job.logger.debug(cmd)
        result = container.client.system(cmd).get()
        if result.state != 'SUCCESS':
            raise j.exceptions.RuntimeError("Failed to run zeroctl list {} {}".format(result.stdout, result.stderr))
        return {vdisk.strip("lba:") for vdisk in result.stdout.splitlines()}
    finally:
        container.stop()


def monitor(job):
    import time
    from zeroos.orchestrator.configuration import get_jwt_token_from_job
    job.context['token'] = get_jwt_token_from_job(job)
    service = job.service

    if service.model.actionsState['install'] != 'ok':
        return

    if service.model.data.clusterType == "object":
        return

    healthcheck_service = job.service.aysrepo.serviceGet(role='healthcheck', instance='storage_cluster_%s' % service.name, die=False)
    if healthcheck_service is None:
        healthcheck_actor = service.aysrepo.actorGet('healthcheck')
        healthcheck_service = healthcheck_actor.serviceCreate(instance='storage_cluster_%s' % service.name)
        service.consume(healthcheck_service)

    # Get orphans
    total_disks = list_vdisks(job)
    vdisk_services = service.aysrepo.servicesFind(role='vdisk', producer="%s!%s" % (service.model.role, service.name))
    nonorphans = {disk.name for disk in vdisk_services if disk.model.data.status != "orphan"}

    old_orphans_services = {disk for disk in vdisk_services if disk.model.data.status == "orphan"}

    old_orphans = set()
    for orphan_service in old_orphans_services:
        # Delete orphan vdisk if operator didn't act for 7 days
        orphan_time = (int(time.time()) - orphan_service.model.data.timestamp) / (3600 * 24)
        if orphan_time >= 7:
            j.tools.async.wrappers.sync(orphan_service.executeAction('delete', context=job.context))
            j.tools.async.wrappers.sync(orphan_service.delete())
            continue
        old_orphans.add(orphan_service.name)

    new_orphans = total_disks - nonorphans
    total_orphans = new_orphans | old_orphans

    for orphan in new_orphans:
        actor = service.aysrepo.actorGet('vdisk')
        args = {
            "status": "orphan",
            "timestamp": int(time.time()),
            "storageCluster": service.name,
        }
        actor.serviceCreate(instance=orphan, args=args)

    healthcheck = {
        "id": "storageclusters",
        "name": "storagecluster orphan vdisk report",
        "messages": [],
    }
    for orphan in total_orphans:
        healthcheck["messages"].append({
            "id": orphan,
            "status": "WARNING",
            "text": "Orphan vdisk %s is found" % orphan,
        })
    update_healthcheck(job, healthcheck_service, healthcheck)


def update_healthcheck(job, health_service, healthchecks):
    import time

    service = job.service

    interval = service.model.actionGet('monitor').period
    new_healthchecks = list()
    if not isinstance(healthchecks, list):
        healthchecks = [healthchecks]
    defaultresource = '/storageclusters/{}'.format(service.name)
    for health_check in healthchecks:
        for health in health_service.model.data.healthchecks:
            # If this healthcheck already exists, update its attributes
            if health.id == health_check['id']:
                health.name = health_check.get('name', '')
                health.resource = health_check.get('resource', defaultresource) or defaultresource
                health.messages = health_check.get('messages', [])
                health.category = health_check.get('category', '')
                health.lasttime = time.time()
                health.interval = interval
                health.stacktrace = health_check.get('stacktrace', '')
                break
        else:
            # healthcheck doesn't exist in the current list, add it to the list of new
            health_check['lasttime'] = time.time()
            health_check['interval'] = interval
            new_healthchecks.append(health_check)

    old_healthchecks = health_service.model.data.to_dict().get('healthchecks', [])
    old_healthchecks.extend(new_healthchecks)
    health_service.model.data.healthchecks = old_healthchecks


def addStorageServer(job):
    raise NotImplementedError()


def reoveStorageServer(job):
    raise NotImplementedError()
