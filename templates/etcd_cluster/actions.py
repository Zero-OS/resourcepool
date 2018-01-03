from js9 import j


def input(job):
    if job.model.args.get('etcds', []) != []:
        raise j.exceptions.Input("etcds should not be set as input")

    nodes = job.model.args.get('nodes', [])
    if not nodes:
        raise j.exceptions.Input("Invalid amount of nodes provided")


def init(job):
    configure(job)


def ensureStoragepool(job, node):
    """
    param: job  ,, currently executing job object
    param: node ,, node object from the zeroos.orchestrator.sal library
    """
    from zeroos.orchestrator.sal.StoragePool import StoragePools
    from zeroos.orchestrator.utils import find_disks
    service = job.service

    # prefer nvme if not then ssd if not then just use the cache what ever it may be
    free_disks = find_disks('nvme', [node], 'sp_etcd_')
    if not free_disks[node.name]:
        free_disks = find_disks('ssd', [node], 'sp_etcd_')
        if not free_disks[node.name]:
            return "{}_fscache".format(node.name)

    # choose the first choice in the results since create takes a list we choose the first item and create a list with it.
    devices = [free_disks[node.name][0].devicename]
    storagePool = StoragePools(node).create('etcd_%s' % service.name, devices, 'single', 'single')
    storagePool.mount()
    storagePoolService = storagePool.ays.create(service.aysrepo)
    return storagePoolService.name


def configure(job):
    import random
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token
    from zeroos.orchestrator.configuration import get_configuration

    service = job.service
    job.context['token'] = get_jwt_token(job.service.aysrepo)
    config = get_configuration(service.aysrepo)

    nodes = set()
    for node_service in service.producers['node']:
        nodes.add(Node.from_ays(node_service, job.context['token']))
    nodes = list(nodes)

    if len(nodes) % 2 == 0:
        nodes = random.sample(nodes, len(nodes) - 1)

    etcd_actor = service.aysrepo.actorGet("etcd")
    container_actor = service.aysrepo.actorGet("container")
    fsactor = service.aysrepo.actorGet("filesystem")
    etcd_args = {}
    peers = []
    etcds = []
    flist = config.get('etcd-flist', 'https://hub.gig.tech/gig-official-apps/etcd-release-3.2.flist')
    for node in nodes:
        baseports, tcpservices = get_baseports(job, node, baseport=2379, nrports=2)
        containername = '{}_{}_{}_{}'.format(service.name, 'etcd', node.name, baseports[1])

        args = {
            'storagePool': ensureStoragepool(job, node),
            'name': containername,
        }
        old_filesystem_service = service.aysrepo.servicesFind(name=containername, role='filesystem')
        if old_filesystem_service:
            node.client.filesystem.remove('/mnt/storagepools/%s/filesystems/%s/member' % (args['storagePool'], containername))
        fsactor.serviceCreate(instance=containername, args=args)

        # create container
        data_dir = '/mnt/data'
        args = {
            'node': node.name,
            'flist': flist,
            'mounts': [{'filesystem': containername, 'target': data_dir}],
            'hostNetworking': True,
        }
        container_actor.serviceCreate(instance=containername, args=args)

        server_bind = '{}:{}'.format(node.storageAddr, baseports[1])
        client_bind = '{}:{}'.format(node.storageAddr, baseports[0])
        mgmt_client_bind = '{}:{}'.format(node.addr, baseports[0])
        etcd_args[node.name] = {
            "serverBind": server_bind,
            "clientBind": client_bind,
            "container": containername,
            "mgmtClientBind": mgmt_client_bind,
            "tcps": tcpservices,
            "homeDir": data_dir,
        }
        etcdID = "{}_{}_{}".format(service.name, node.name, baseports[1])
        if service.aysrepo.servicesFind(name=etcdID, role='etcd'):
            etcdID = "%s_recovered" % etcdID
        peers.append("{}=http://{}".format(etcdID, server_bind))

    for k, v in etcd_args.items():
        tcps = v.pop("tcps")
        etcdname = "{}_{}_{}".format(service.name, k, tcps[1].model.data.port)
        if service.aysrepo.servicesFind(name=etcdname, role='etcd'):
            etcdname = "%s_recovered" % etcdname
        v["peers"] = peers
        etcd_service = etcd_actor.serviceCreate(instance=etcdname, args=v)
        etcd_service.consume(tcps[0])
        etcd_service.consume(tcps[1])
        etcds.append(etcd_service.name)
        service.consume(etcd_service)
    service.model.data.etcds = etcds


def install(job):
    service = job.service
    service.model.data.status = "running"
    service.saveAll()


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


def check_container_etcd_status(job, etcd):
    '''
    checks status of both container and etcd , since we cannot check status of etcd without the container being running
    param job,, job called on the watchdog_handler action
    param etcd,, container etcd
    '''
    try:
        container = etcd.parent
        container_client, container_status = check_container_status(job, container)
        if container_status:
            container_client.client.job.list("etcd.{}".format(etcd.name))
            return True, True
        return False, False
    except RuntimeError as e:
        return True, False


def check_container_status(job, container):
    '''
    checks status of the container and avoids throwing errors if node is down
    param job,, job called on the watchdog_handler action
    param container,, container service
    '''
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    try:
        container_client = Container.from_ays(container,
                                              password=job.context['token'],
                                              logger=job.service.logger,
                                              timeout=5)
        if container_client.id:
            # if returns empty means the container is down
            return container_client, True
        return None, False
    except ConnectionError as e:
        # to catch exception if node is down
        return None, False


def watchdog_handler(job):
    '''
    This action is called upon from either a container or etcd watchdog handler which are called from node service's
    watchdog. This self heals the etcd cluster if etcd fails will redeploy, if container fails will redeploy and if the
    cluster goes into disaster where the number of etcd dead > (n-1)/2 then the action will redeploy the cluster on the
    nodes availabe on the enviroment and resave the configurations in the storage clusters and the vdisks .
    '''
    import asyncio

    async def selfhealing(job):
        from zeroos.orchestrator.sal.Node import Node
        from zeroos.orchestrator.configuration import get_jwt_token
        import redis
        # needs refactoring : for refacotr the disabled services will be detected by the service's own watchdog handler
        # so here can focus on only the recovery

        service = job.service
        if service.model.data.status == 'recovering':
            return

        if not service.aysrepo.servicesFind(role='node'):
            return

        service.model.data.status = 'recovering'
        etcds = set(service.producers.get('etcd', []))
        working_etcds = set()
        dead_nodes = set()
        dead_etcds_working_containers = set()
        working_model_nodes = set()
        token = get_jwt_token(job.service.aysrepo)
        job.context['token'] = token
        service.saveAll()

        # check on etcd container since the watch dog will handle the actual service
        for etcd in etcds:
            container_status, etcd_status = check_container_etcd_status(job, etcd)
            if not etcd_status and container_status:
                dead_etcds_working_containers.add(etcd)

            if etcd_status:
                working_etcds.add(etcd)

        dead_etcds_containers = etcds-working_etcds

        for etcd in dead_etcds_containers:
            container = etcd.parent
            node = container.parent
            try:
                node_client = Node.from_ays(node, password=token, timeout=20)
                ping = node_client.client.ping()
                working_model_nodes.add(node)
            except (redis.TimeoutError, ConnectionError) as e:
                ping = None
                dead_nodes.add(node.name)

            # check if less than disaster threshold do normal respawn of single etcd or container and etcd
            if len(working_etcds) > (len(etcds)-1)/2:
                # respawn dead etcd only
                for etcd in dead_etcds_working_containers:
                    await etcd.asyncExecuteAction('start', context=job.context)
                    service.model.data.status = 'running'
                    service.saveAll()
                    service.logger.info("etcd %s respwaned" % etcd.name)
                    return
                # respawn dead containers
                if not ping:
                    raise j.exceptions.RunTimeError("node %s with Etcd %s is down" % (node.name, etcd.name))
                await container.asyncExecuteAction('start', context=job.context)
                service.model.data.status = 'running'
                await etcd.asyncExecuteAction('start', context=job.context)
                service.saveAll()
                service.logger.info("etcd %s and container %s respawned" % (etcd.name, container.name))
                return

        # stop all remaining containers from the old cluster
        try:
            for etcd in working_etcds:
                await etcd.asyncExecuteAction('stop', context=job.context)
                await etcd.parent.asyncExecuteAction('stop', context=job.context)

            # clean all reaminag tcps on old  running nodes
            for etcd in service.producers['etcd']:
                for tcp in etcd.producers['tcp']:
                    try:
                        Node.from_ays(etcd.parent.parent, password=token, timeout=5)
                        await tcp.asyncExecuteAction('drop', context=job.context)
                    except ConnectionError:
                        continue
                    await tcp.asyncExecuteAction('delete', context=job.context)

            # check if nodes are more than the min number for cluster deployment which is 3.
            tmp = list()
            for node in [service for service in service.aysrepo.servicesFind(role='node')]:
                if node.model.data.status == 'running':
                    tmp.append(node.name)

            all_nodes = set(tmp)
            if len(working_model_nodes) > 1:
                service.model.data.nodes = [node.name for node in working_model_nodes]
            else:
                service.model.data.nodes = list(all_nodes - dead_nodes)

            # remove old nodes and etcds from producers (has tobe here)
            for etcd_service in service.producers['etcd']:
                service.model.producerRemove(etcd_service)
                service.saveAll()

            for node_service in service.producers['node']:
                if node_service.name not in service.model.data.nodes:
                    service.model.producerRemove(node_service)
                    service.saveAll()

            # consume new nodes.
            node_services = [service.aysrepo.serviceGet(instance=node, role='node')for node in service.model.data.nodes]
            for node_service in node_services:
                service.consume(node_service)

            service.model.data.etcds = []
            service.saveAll()

            await service.asyncExecuteAction('configure', context=job.context)

            # install all services created by the configure of the etcd_cluster
            etcd_services = [service.aysrepo.serviceGet(instance=i, role='etcd') for i in service.model.data.etcds]
            for etcd in etcd_services:
                for mount in etcd.parent.model.data.mounts:
                    fs = service.aysrepo.serviceGet('filesystem', mount.filesystem)
                    await fs.asyncExecuteAction('install', context=job.context)
                for tcp in etcd.producers['tcp']:
                    await tcp.asyncExecuteAction('install',  context=job.context)
                await etcd.parent.asyncExecuteAction('install', context=job.context)
                await etcd.asyncExecuteAction('install', context=job.context)

            # save all vdisks to new etcd cluster
            vdisks = service.aysrepo.servicesFind(role='vdisk')
            for vdisk in vdisks:
                vdisk.asyncExecuteAction('save_config', context=job.context)

            # save all storage cluster to new etcd cluster
            storagecluster_block_services = service.aysrepo.servicesFind(role='storagecluster.block')
            for storagecluster_block_service in storagecluster_block_services:
                await storagecluster_block_service.asyncExecuteAction('save_config', context=job.context)

            storagecluster_object_services = service.aysrepo.servicesFind(role='storagecluster.object')
            for storagecluster_object_service in storagecluster_object_services:
                await storagecluster_object_service.asyncExecuteAction('save_config', context=job.context)

            # restart all runnning vms
            vmachines = service.aysrepo.servicesFind(role='vm')
            for vmachine in vmachines:
                if vmachine.model.data.status == 'running':
                    await vmachine.asyncExecuteAction('start', context=job.context)
        finally:
            service.model.data.status = 'running'
            service.saveAll()

        for etcd_service in service.aysrepo.servicesFind(role='etcd'):
            if etcd_service.model.data.status != 'running':
                container_status, etcd_status = check_container_etcd_status(job, etcd_service.parent)
                if not etcd_status:
                    await etcd_service.parent.asyncExecuteAction('delete', context=job.context)
        service.logger.info("etcd_cluster  %s respawned" % service.name)
    loop = job.service._loop
    asyncio.ensure_future(selfhealing(job), loop=loop)
