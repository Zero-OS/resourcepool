from js9 import j


def input(job):
    if job.model.args.get('etcds', []) != []:
        raise j.exceptions.Input("etcds should not be set as input")

    nodes = job.model.args.get('nodes', [])
    if not nodes:
        raise j.exceptions.Input("Invalid amount of nodes provided")


def init(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction("configure", context=job.context))


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
            'storagePool': "{}_fscache".format(node.name),
            'name': containername,
        }
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
        peers.append("{}_{}_{}=http://{}".format(service.name, node.name, baseports[1], server_bind))

    for k, v in etcd_args.items():
        tcps = v.pop("tcps")
        etcdname = "{}_{}_{}".format(service.name, k, tcps[1].model.data.port)
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

def watchdog_handler(job):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.ETCD import ETCD
    from zeroos.orchestrator.configuration import get_jwt_token
    import redis

    service = job.service
    if service.model.data.status == 'recovering':
        return
    service.model.data.status = 'recovering'
    service.saveAll()
    etcds = set(service.producers.get('etcd', []))
    working_etcds = set()
    dead_nodes = set()
    dead_etcds = set()
    working_model_nodes = set()
    token = get_jwt_token(job.service.aysrepo)
    
    # check on etcd container since the watch dog will handle the actual service
    for etcd in etcds:
        container = etcd.parent
        node = container.parent
        try:
            container_client = Container.from_ays(container, password=token)
            if container_client.id:
                container_client.client.job.list("etcd.{}".format(etcd.name))
        except ConnectionError as e:
            container_client = None
        except RuntimeError as e:
            dead_etcds.add(etcd)
        if container_client and container_client.id:
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

        if len(working_etcds) > (len(etcds)-1)/2:
            # dead etcds only 
            for etcd in dead_etcds:
                if len(working_etcds) > (len(etcds)-1)/2:
                    j.tools.async.wrappers.sync(etcd.executeAction('start', context=job.context))
                    return
            # dead containers 
            if not ping:
                raise j.exceptions.RunTimeError("node %s with Etcd %s is down" % (node.name, etcd.name))
            j.tools.async.wrappers.sync(container.executeAction('start', context=job.context))
            j.tools.async.wrappers.sync(etcd.executeAction('start', context=job.context))
            return

    # clean all remaining etcds from the old cluster
    for etcd in working_etcds:
        container = etcd.parent
        j.tools.async.wrappers.sync(etcd.executeAction('stop', context=job.context))
        j.tools.async.wrappers.sync(etcd.delete())
        j.tools.async.wrappers.sync(container.executeAction('stop', context=job.context))
        j.tools.async.wrappers.sync(container.delete())

    # clean all reaminag tcps on old  running nodes
    for etcd in service.producers['etcd']:
        for tcp in etcd.producers['tcp']:
            try:
                Node.from_ays(etcd.parent.parent, password=token)
                j.tools.async.wrappers.sync(tcp.executeAction('drop', context=job.context))
            except ConnectionError:
                continue
            j.tools.async.wrappers.sync(tcp.delete())

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
    j.tools.async.wrappers.sync(service.executeAction('configure', context=job.context))

    # install all services created by the configure of the etcd_cluster
    etcd_services = [service.aysrepo.serviceGet(instance=i, role='etcd') for i in service.model.data.etcds]
    for etcd in etcd_services:
        for mount in etcd.parent.model.data.mounts:
            fs = service.aysrepo.serviceGet('filesystem', mount.filesystem)
            j.tools.async.wrappers.sync(fs.executeAction('install', context=job.context))
        for tcp in etcd.producers['tcp']:
            j.tools.async.wrappers.sync(tcp.executeAction('install',  context=job.context))
        j.tools.async.wrappers.sync(etcd.parent.executeAction('install', context=job.context))
        j.tools.async.wrappers.sync(etcd.executeAction('install', context=job.context))

    # save all vdisks to new etcd cluster
    vdisks = service.aysrepo.servicesFind(role='vdisk')
    for vdisk in vdisks:
        j.tools.async.wrappers.sync(vdisk.executeAction('save_config', context=job.context))

    # save all storage cluster to new etcd cluster
    storage_clusters = service.aysrepo.servicesFind(role='storage_cluster')
    for storage_cluster in storage_clusters:
        j.tools.async.wrappers.sync(storage_cluster.executeAction('save_config', context=job.context))

    # restart all runnning vms
    vmachines = service.aysrepo.servicesFind(role='vm')
    for vmachine in vmachines:
        if vmachine.model.data.status == 'running':
            j.tools.async.wrappers.sync(vmachine.executeAction('start', context=job.context))

    service.model.data.status = 'running'
    service.saveAll()