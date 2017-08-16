from js9 import j


def input(job):
    if job.model.args.get('etcds', []) != []:
        raise j.exceptions.Input("etcds should not be set as input")

    nodes = job.model.args.get('nodes', [])
    if not nodes:
        raise j.exceptions.Input("Invalid amount of nodes provided")


def init(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction("configure", context=job.context))


def configure(job):
    import random
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token
    from zeroos.orchestrator.configuration import get_configuration

    service = job.service
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
        etcd_args[node.name] = {
            "serverBind": server_bind,
            "clientBind": client_bind,
            "container": containername,
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
        service.consume(etcd_service)


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

    service = job.service
    etcds = set(service.producers.get('etcd', []))
    working_etcds = set()
    token = get_jwt_token(job.service.aysrepo)
    
    # check on etcd container since the watch dog will handle the actual service 
    for etcd in etcds:
        container = etcd.parent
        node = container.parent
        container_client = Container.from_ays(container, password=token)
        if container_client.id:
            working_etcds.add(etcd)

    dead_etcds = etcds-working_etcds

    if len(working_etcds) >= (len(etcds)-1)/2:
        for etcd in etcds-working_etcds:
            container = etcd.parent
            node = container.parent
            container_client = Container.from_ays(container, password=token)
            node_client = Node.from_ays(node, password=token)
            if not node_client.client.ping():
                raise j.exceptions.RunTimeError("node %s with Etcd %s is down" % (node.name, etcd.name))

            j.tools.async.wrappers.sync(container.executeAction('start', context=job.context))
            j.tools.async.wrappers.sync(etcd.executeAction('start', context=job.context))
        return
    if not working_etcds:
        raise j.exceptions.RunTimeError("No Etcds left to recover from, etcd_cluster %s is down" % service.name)

    respawned_container_nodes = []

    for dead_etcd in dead_etcds:
        container = dead_etcd.parent
        node = container.parent
        if node_client.client.ping():
            working_etcd = working_etcds[0]    
            etcd = ETCD.from_ays(working_etcd, password=token)
            containername = '{}_{}_{}_*'.format(service.name, 'etcd', node.name)
            dead_container = service.aysrepo.servicesFind(name=containername, role='container')
            j.tools.async.wrappers.sync(dead_container.executeAction('start', context=job.context))
            etcd.recover("/mnt/data/", working_etcd.parent, dead_container)
            respawned_container_nodes.append(node.name)
                    
    all_nodes = service.model.data.nodes
    service.model.data.nodes = respawned_container_nodes
    service.saveAll()
    j.tools.async.wrappers.sync(service.executeAction('configure', context=job.context))
    service.model.data.nodes = all_nodes
    service.saveAll()