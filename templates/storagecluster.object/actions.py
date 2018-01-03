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

    servers_per_meta = job.model.args.get("serversPerMetaDrive", 0)
    if not servers_per_meta:
        raise ValueError('serversPerMetaDrive should be larger than 0')

    serverpernode = nrserver // len(nodes)
    if servers_per_meta > serverpernode:
        raise ValueError('Invalid amount of serversPerMetaDrive, should be less or equal to the number of servers per node')

    check_zerostor_config(job)

    data_shards = job.model.args.get("dataShards", 0)
    parity_shards = job.model.args.get("parityShards", 0)
    if not data_shards or not parity_shards:
        raise j.exceptions.Input("dataShards and parityShards should be larger than 0")
    if (data_shards + parity_shards) > nrserver:
        raise j.exceptions.Input("dataShards and parityShards should be greater than or equal to number of servers")

    etcd_clusters = job.service.aysrepo.servicesFind(role='etcd_cluster')
    if not etcd_clusters:
        raise j.exceptions.Input('No etcd cluster service found.')

    return job.model.args


def check_zerostor_config(job):
    import requests

    zstor_organization = job.model.args.get('zerostorOrganization', None)
    zstor_namespace = job.model.args.get('zerostorNamespace', None)
    zstor_clientid = job.model.args.get('zerostorClientID', None)
    zstor_clientsecret = job.model.args.get('zerostorSecret', None)

    if not (zstor_organization and zstor_namespace and zstor_clientid and zstor_clientsecret):
        raise ValueError('Missing 0-stor configuration')

    url = "https://itsyou.online/v1/oauth/access_token"
    scope = "user:memberof:{org}.0stor.{namespace}.read,user:memberof:{org}.0stor.{namespace}.write,user:memberof:{org}.0stor.{namespace}.delete"
    scope = scope.format(
        org=zstor_organization,
        namespace=zstor_namespace
    )
    params = {
        "client_id": zstor_clientid,
        "client_secret": zstor_clientsecret,
        "grant_type": "client_credentials",
        "response_type": "id_token",
        "scope": scope,
    }
    res = requests.post(url, params=params)
    if res.status_code != 200:
        raise ValueError("Invalid itsyouonline configuration")


def get_cluster(job):
    from zeroos.orchestrator.configuration import get_jwt_token
    from zeroos.orchestrator.sal.StorageCluster import ObjectCluster

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    return ObjectCluster.from_ays(job.service, job.context['token'])


def init(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.StorageCluster import ObjectCluster
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context["token"] = get_jwt_token(job.service.aysrepo)

    service = job.service
    nodes = set()
    for node_service in service.producers["node"]:
        nodes.add(Node.from_ays(node_service, job.context["token"]))
    nodes = list(nodes)
    nodemap = {node.name: node for node in nodes}

    data_available_disks = get_availabledisks(job, service.model.data.dataDiskType)

    if service.model.data.dataDiskType == service.model.data.metaDiskType:
        meta_available_disks = data_available_disks
    else:
        meta_available_disks = get_availabledisks(job, service.model.data.metaDiskType)

    storagecluster_sal = ObjectCluster.from_ays(service, job.context["token"])
    datadisks, metadisks = storagecluster_sal.get_disks(data_available_disks, meta_available_disks)

    # lets create some services
    spactor = service.aysrepo.actorGet("storagepool")
    fsactor = service.aysrepo.actorGet("filesystem")
    containeractor = service.aysrepo.actorGet("container")
    zerostorActor = service.aysrepo.actorGet("zerostor")

    filesystems = []
    zerostors = []

    def create_server(node, datadisk, metadisk, baseport, tcp):
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

        containername = '{}_{}'.format(storagepoolname, baseport)
        # adding filesystem
        args = {
            'storagePool': storagepoolname,
            'name': containername,
        }
        filesystems.append(fsactor.serviceCreate(instance=containername, args=args))
        config = get_configuration(job.service.aysrepo)

        metastoragepoolname = 'cluster_{}_{}_{}'.format(node.name, service.name, metadisk.name)
        if not service.aysrepo.serviceGet(role='storagepool', instance=metastoragepoolname, die=False):
            diskmap = [{'device': metadisk.devicename}]
            args = {
                'node': node.name,
                'metadataProfile': 'single',
                'dataProfile': 'single',
                'devices': diskmap
            }
            metaspservice = spactor.serviceCreate(instance=metastoragepoolname, args=args)
            service.consume(metaspservice)

        metacontainername = '{}_{}_meta'.format(metastoragepoolname, baseport)
        # adding filesystem
        args = {
            'storagePool': metastoragepoolname,
            'name': metacontainername,
        }
        fs = fsactor.serviceCreate(instance=metacontainername, args=args)
        filesystems.append(fs)
        service.consume(fs)

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
        zerostors.append(zerostorService)

    servers_per_meta = service.model.data.serversPerMetaDrive
    for nodename, disks in datadisks.items():
        node = nodemap[nodename]
        # making the storagepool
        nrports = len(disks)
        baseports, tcpservices = get_baseports(job, node, baseport=2000, nrports=nrports)
        for idx, disk in enumerate(disks):
            metadisk = metadisks[nodename][idx // servers_per_meta]
            create_server(node=node,
                          datadisk=disk,
                          metadisk=metadisk,
                          baseport=baseports[idx],
                          tcp=tcpservices[idx])

    service.model.data.init('filesystems', len(filesystems))
    service.model.data.init('storageServers', len(zerostors))

    for index, fs in enumerate(filesystems):
        service.consume(fs)
        service.model.data.filesystems[index] = fs.name
    for index, zerostor in enumerate(zerostors):
        service.consume(zerostor)
        service.model.data.storageServers[index] = zerostor.name

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
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    etcd_clusters = job.service.aysrepo.servicesFind(role='etcd_cluster')
    if not etcd_clusters:
        j.exceptions.RuntimeError('No etcd cluster found')

    etcd_cluster = etcd_clusters[0]
    etcd = EtcdCluster.from_ays(etcd_cluster, job.context['token'])

    # Push zerostorconfig to etcd
    zerostor_services = service.producers["zerostor"]
    zstor_organization = service.model.data.zerostorOrganization
    zstor_namespace = service.model.data.zerostorNamespace
    zstor_clientid = service.model.data.zerostorClientID
    zstor_clientsecret = service.model.data.zerostorSecret

    zerostor_config = {
        "iyo": {
            "org": zstor_organization,
            "namespace": zstor_namespace,
            "clientID": zstor_clientid,
            "secret": zstor_clientsecret,
        },
        "dataServers": [{"address": zservice.model.data.bind} for zservice in zerostor_services],
        "metadataServers": [{"address": dialstring} for dialstring in etcd.dialstrings.split(",")],
        "dataShards": service.model.data.dataShards,
        "parityShards": service.model.data.parityShards,
    }
    yamlconfig = yaml.safe_dump(zerostor_config, default_flow_style=False)
    etcd.put(key="%s:cluster:conf:zerostor" % service.name, value=yamlconfig)


def delete_config(job):
    from zeroos.orchestrator.sal.ETCD import EtcdCluster

    service = job.service
    etcd_clusters = job.service.aysrepo.servicesFind(role='etcd_cluster')
    if not etcd_clusters:
        j.exceptions.RuntimeError('No etcd cluster found')

    etcd_cluster = etcd_clusters[0]
    etcd = EtcdCluster.from_ays(etcd_cluster, job.context['token'])

    etcd.delete(key="%s:cluster:conf:zerostor" % service.name)


def get_availabledisks(job, disktype):
    from zeroos.orchestrator.sal.StorageCluster import ObjectCluster
    from zeroos.orchestrator.utils import find_disks

    service = job.service

    used_disks = {}
    for node in service.model.data.nodes:
        disks = set()
        pools = service.aysrepo.servicesFind(role='storagepool', parent='node.zero-os!%s' % node)
        for pool in pools:
            devices = {device.device for device in pool.model.data.devices}
            disks.update(devices)
        used_disks[node] = disks

    cluster = ObjectCluster.from_ays(service, job.context['token'])
    partition_name = 'sp_cluster_{}'.format(cluster.name)
    availabledisks = find_disks(disktype, cluster.nodes, partition_name)
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
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    dashboardsrv = job.service.aysrepo.serviceGet(role='dashboard', instance=job.service.name, die=False)
    if dashboardsrv:
        cluster = get_cluster(job)
        dashboardsrv.model.data.dashboard = cluster.dashboard
        dashboardsrv.executeAction('install', context=job.context)

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
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    zerostors = service.producers.get("zerostor", [])
    for zerostor in zerostors:
        zerostor.executeAction("stop", context=job.context)


def delete(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    job.service.model.data.status = "halting"

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    zerostors = service.producers.get('zerostor', [])
    pools = service.producers.get('storagepool', [])
    filesystems = service.producers.get('filesystem', [])

    for storageEngine in zerostors:
        tcps = storageEngine.producers.get('tcp', [])
        for tcp in tcps:
            tcp.executeAction('drop', context=job.context)
            tcp.delete()

        container = storageEngine.parent
        container.executeAction('stop', context=job.context)
        container.delete()

    for filesystem in filesystems:
        filesystem.executeAction('delete', context=job.context)
        filesystem.delete()

    for pool in pools:
        pool.executeAction('delete', context=job.context)
        pool.delete()

    delete_config(job)
    job.logger.info("stop cluster {}".format(service.name))
    job.service.model.data.status = 'empty'


def monitor(job):
    from zeroos.orchestrator.sal.StorageCluster import ObjectCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service

    if service.model.actionsState['install'] != 'ok':
        return

    cluster = ObjectCluster.from_ays(service, job.context['token'])
    if service.model.data.status == 'ready' and not cluster.is_running():
        cluster.start()


def addStorageServer(job):
    raise NotImplementedError()


def reoveStorageServer(job):
    raise NotImplementedError()
