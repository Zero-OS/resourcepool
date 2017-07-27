def input(job):
    from js9 import j
    if job.model.args.get('etcds', []) != []:
        raise j.exceptions.Input("etcds should not be set as input")

    nodes = job.model.args.get('nodes', [])
    size = job.model.args.get('size', 0)

    if size % 2 == 0:
        raise j.exceptions.Input("Size should be odd number")

    if size > len(nodes) != 0:
        raise j.exceptions.Input("Invalid amount of nodes provided")


def init(job):
    import random
    from zeroos.orchestrator.sal.Node import Node
    service = job.service
    nodes = set()
    for node_service in service.producers['node']:
        nodes.add(Node.from_ays(node_service, job.context['token']))
    nodes = list(nodes)

    nodes = random.sample(nodes, service.model.data.size)
    etcd_actor = service.aysrepo.actorGet("etcd")
    container_actor = service.aysrepo.actorGet("container")
    etcd_args = {}
    peers = []
    for node in nodes:
        baseports, tcpservices = get_baseports(job, node, baseport=2379, nrports=2)
        containername = '{}_{}_{}_{}'.format(service.name, 'etcd', node.name, baseports[1])
        # create container
        args = {
            'node': node.name,
            'flist': 'https://hub.gig.tech/gig-official-apps/etcd-release-3.2.flist',
            'hostNetworking': True,
        }
        container_actor.serviceCreate(instance=containername, args=args)

        server_bind = '{}:{}'.format(node.storageAddr, baseports[1])
        client_bind = '{}:{}'.format(node.storageAddr, baseports[0])
        etcd_args[node.name] = {
            "serverBind": server_bind,
            "clientBind": client_bind,
            "container": containername,
            "tcps": tcpservices
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
