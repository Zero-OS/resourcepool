from js9 import j


def input(job):
    service = job.service
    # Check the blueprint input for errors
    args = job.model.args
    if args.get('vdisks'):
        raise j.exceptions.Input('vdisks property should not be set in the blueprint. Instead use disks property.')
    disks = args.get("disks", [])
    args['vdisks'] = []
    if disks != []:
        for disk in disks:
            if not disk["vdiskid"]:
                continue
            # make sure this disk is not used anywhere
            vm_services = job.service.aysrepo.servicesFind(actor="vm")
            for vm_service in vm_services:
                for vdisk in vm_service.model.data.vdisks:
                    if vdisk == disk["vdiskid"]:
                        raise j.exceptions.Input('vdisk {vdisk} is used by other machine {vm}'.format(vdisk=vdisk, vm=vm_service.name))

            service.aysrepo.serviceGet(role='vdisk', instance=disk["vdiskid"])
            args['vdisks'].append(disk['vdiskid'])
    return args


def get_node(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    return Node.from_ays(job.service.parent, job.context['token'])


def create_zerodisk_container_service(job, parent):
    """
    first check if the vdisks container for this vm exists.
    if not it creates it.
    return the container service
    """
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    config = get_configuration(service.aysrepo)
    actor = service.aysrepo.actorGet("container")
    args = {
        'node': parent.name,
        'flist': config.get('0-disk-flist', 'https://hub.gig.tech/gig-official-apps/0-disk-master.flist'),
        'hostNetworking': True,
    }
    job.logger.info("create zerodisk container from %s", args['flist'])
    container_name = 'vdisks_{}_{}'.format(service.name, parent.name)
    containerservice = actor.serviceCreate(instance=container_name, args=args)
    # make sure the container has the right parent, the node where this vm runs.
    containerservice.model.changeParent(parent)
    containerservice.executeAction('start', context=job.context)

    return containerservice


def create_service(service, container, role='nbdserver', bind=None, waitListenBind=None, acceptAddress=None):
    """
    first check if the service exists
    if not it creates it.
    return the created service
    """
    if role not in ('nbdserver', 'tlogserver'):
        raise ValueError("role can only be nbdserver or tlogserver")

    service_name = '{}_{}_{}'.format(role, service.name, container.parent.name)

    try:
        created_service = service.aysrepo.serviceGet(role=role, instance=service_name)
    except j.exceptions.NotFound:
        created_service = None

    if created_service is None:
        actor = service.aysrepo.actorGet(role)
        args = {
            'container': container.name,
        }
        if bind:
            args["bind"] = bind
            args["waitListenBind"] = waitListenBind
        if acceptAddress:
            args["acceptAddress"] = acceptAddress
        created_service = actor.serviceCreate(instance=service_name, args=args)
    return created_service


def _init_zerodisk_services(job, nbd_container_service, tlog_container_service=None, tlog_container_sal=None):
    service = job.service
    # Create nbderver service
    nbdserver_service = create_service(service, nbd_container_service)
    job.logger.info("creates nbd server for vm {}".format(service.name))
    service.consume(nbdserver_service)

    if tlog_container_service:
        # Create tlogserver service
        if not tlog_container_sal:
            from zeroos.orchestrator.sal.Container import Container
            tlog_container_sal = Container.from_ays(tlog_container_service, job.context['token'], logger=service.logger)
        ports, tcp = get_baseports(job, tlog_container_sal.node, 11211, 2)
        bind = "%s:%s" % (tlog_container_sal.node.storageAddr, ports[0])
        waitListenBind = "%s:%s" % (tlog_container_sal.node.storageAddr, ports[1])
        tlogserver_service = create_service(service, tlog_container_service, role='tlogserver', bind=bind, waitListenBind=waitListenBind)
        tlogserver_service.consume(tcp[0])
        tlogserver_service.consume(tcp[1])
        job.logger.info("creates tlog server for vm {}".format(service.name))
        service.consume(tlogserver_service)
        nbdserver_service.consume(tlogserver_service)


def _nbd_url(job, container, nbdserver, vdisk):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    container_root = container.info['container']['root']
    node = Node.from_ays(nbdserver.parent.parent, password=job.context['token']).client
    node.filesystem.mkdir("/var/run/nbd-servers/")
    endpoint = nbdserver.model.data.socketPath.lstrip('/')
    socket_path = j.sal.fs.joinPaths(container_root, endpoint)
    link = j.sal.fs.joinPaths("/var/run/nbd-servers/", endpoint)

    result = node.system("ln -sf %s /var/run/nbd-servers/" % socket_path).get()
    if result.state.upper() == "ERROR":
        raise RuntimeError(result.stderr)
    return 'nbd+unix:///{id}?socket={socket}'.format(id=vdisk, socket=link)


def init(job):
    start_dependent_services(job)
    save_config(job)


def start_dependent_services(job):
    import random
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service

    # creates all nbd servers for each vdisk this vm uses
    job.logger.info("creates vdisks container for vm {}".format(service.name))
    services = [node for node in service.aysrepo.servicesFind(role="node") if node.model.data.status != "halted"]

    node = random.choice(services)
    if len(services) > 1 and node.name == service.parent.name:
        node = services.index(node)
        services.pop(node)
        node = random.choice(services)

    tlog_container_service = create_zerodisk_container_service(job, node)
    tlog_container = Container.from_ays(tlog_container_service, job.context['token'], logger=service.logger)

    nbd_container_service = create_zerodisk_container_service(job, service.parent)
    _init_zerodisk_services(job, nbd_container_service, tlog_container_service)


def _start_nbd(job, nbdname=None):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    # get all path to the vdisks serve by the nbdservers
    medias = []
    if not nbdname:
        nbdservers = job.service.producers.get('nbdserver', None)
    else:
        nbdservers = [job.service.aysrepo.serviceGet(role='nbdserver', instance=nbdname)]

    if not nbdservers:
        raise j.exceptions.RuntimeError("Failed to start nbds, no nbds created to start")
    nbdserver = nbdservers[0]
    # build full path of the nbdserver unix socket on the host filesystem
    container = Container.from_ays(nbdserver.parent, job.context['token'], logger=job.service.logger)
    if not container.is_running():
        # start container
        nbdserver.parent.executeAction('start', context=job.context)

    # make sure the nbdserver is started
    nbdserver.executeAction('start', context=job.context)
    for vdisk in job.service.model.data.vdisks:
        url = _nbd_url(job, container, nbdserver, vdisk)
        medias.append({'url': url})
    return medias


def start_tlog(job):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    tlogservers = job.service.producers.get('tlogserver', None)
    if not tlogservers:
        raise j.exceptions.RuntimeError("Failed to start tlogs, no tlogs created to start")
    tlogserver = tlogservers[0]
    # build full path of the tlogserver unix socket on the host filesystem
    container = Container.from_ays(tlogserver.parent, password=job.context['token'], logger=job.service.logger)
    # make sure container is up
    if not container.is_running():
        tlogserver.parent.executeAction('start', context=job.context)

    # make sure the tlogserver is started
    tlogserver.executeAction('start', context=job.context)


def get_media_for_disk(medias, disk):
    from urllib.parse import urlparse
    for media in medias:
        url = urlparse(media['url'])
        if disk['vdiskid'] == url.path.lstrip('/'):
            return media


def format_media_nics(job, medias):
    service = job.service
    nics = []
    for nic in service.model.data.nics:
        nic = nic.to_dict()
        nic['hwaddr'] = nic.pop('macaddress', None)
        nics.append(nic)
    for disk in service.model.data.disks:
        if disk.maxIOps > 0:
            media = get_media_for_disk(medias, disk.to_dict())
            media['iotune'] = {'totaliopssec': disk.maxIOps,
                               'totaliopssecset': True}
    return medias, nics


def install(job):
    import time
    from zeroos.core0.client.client import ResultError
    from zeroos.orchestrator.utils import Write_Status_code_Error
    service = job.service
    node = get_node(job)

    # get all path to the vdisks serve by the nbdservers
    start_tlog(job)
    medias = _start_nbd(job)

    job.logger.info("create vm {}".format(service.name))

    media, nics = format_media_nics(job, medias)

    kvm = get_domain(job)
    if not kvm:
        try:
            node.client.kvm.create(
                service.name,
                media=media,
                cpu=service.model.data.cpu,
                memory=service.model.data.memory,
                nics=nics,
            )
        except ResultError as e:
            Write_Status_code_Error(job, e)
            cleanupzerodisk(job)
            service.saveAll()
            raise j.exceptions.Input(str(e))

        # wait for max 60 seconds for vm to be running
        start = time.time()
        while start + 60 > time.time():
            kvm = get_domain(job)
            if kvm:
                service.model.data.vnc = kvm['vnc']
                if kvm['vnc'] != -1:
                    if node.client.nft.rule_exists(kvm['vnc']):
                        break
                    node.client.nft.open_port(kvm['vnc'])
                break
            else:
                time.sleep(3)
        else:
            service.model.data.status = 'error'
            cleanupzerodisk(job)
            raise j.exceptions.RuntimeError("Failed to start vm {}".format(service.name))
    service.model.data.status = 'running'
    service.saveAll()


def start(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    service.model.data.status = 'starting'
    service.saveAll()
    service.executeAction('install', context=job.context)


def get_domain(job):
    node = get_node(job)
    for kvm in node.client.kvm.list():
        if kvm['name'] == job.service.name:
            return kvm


def stop(job):
    service = job.service
    job.logger.info("stop vm {}".format(service.name))
    node = get_node(job)
    kvm = get_domain(job)
    if kvm:
        node.client.kvm.destroy(kvm['uuid'])
    if job.model.args.get('cleanup', None) is not False:
        cleanupzerodisk(job)


def reset(job):
    service = job.service
    job.logger.info("reset vm {}".format(service.name))
    node = get_node(job)
    kvm = get_domain(job)
    if kvm:
        node.client.kvm.reset(kvm['uuid'])


def destroy(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    job.service.executeAction('stop', context=job.context)
    service = job.service
    tlogservers = service.producers.get('tlogserver', [])
    nbdservers = service.producers.get('nbdserver', [])

    parentservices = {}

    for tlogserver in tlogservers:
        parent = tlogserver.parent
        if parent.model.key not in parentservices:
            parentservices[parent.model.key] = parent
        tlogserver.delete()

    for nbdserver in nbdservers:
        parent = nbdserver.parent
        if parent.model.key not in parentservices:
            parentservices[parent.model.key] = parent
        nbdserver.delete()

    for parent in parentservices.values():
        parent.delete()


def cleanupzerodisk(job):
    from zeroos.orchestrator.configuration import get_jwt_token
    from zeroos.orchestrator.sal.Node import Node

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    node = Node.from_ays(service.parent, password=job.context['token'])
    for nbdserver in service.producers.get('nbdserver', []):
        job.logger.info("stop nbdserver for vm {}".format(service.name))
        # make sure the nbdserver is stopped
        nbdserver.executeAction('stop', context=job.context)

    for tlogserver in service.producers.get('tlogserver', []):
        job.logger.info("stop tlogserver for vm {}".format(service.name))
        # make sure the tlogserver is stopped
        tlogserver.executeAction('stop', context=job.context)

    job.logger.info("stop vdisks container for vm {}".format(service.name))
    try:
        container_name = 'vdisks_{}_{}'.format(service.name, service.parent.name)
        container = service.aysrepo.serviceGet(role='container', instance=container_name)
        container.executeAction('stop', context=job.context)
    except j.exceptions.NotFound:
        job.logger.info("container doesn't exists.")

    service.model.data.status = 'halted'

    node = get_node(job)

    vnc = service.model.data.vnc
    if vnc != -1:
        node.client.nft.drop_port(vnc)
        service.model.data.vnc = -1

    service.saveAll()


def pause(job):
    service = job.service
    job.logger.info("pause vm {}".format(service.name))
    node = get_node(job)
    kvm = get_domain(job)
    if kvm:
        node.client.kvm.pause(kvm['uuid'])
        service.model.data.status = 'paused'
        service.saveAll()


def resume(job):
    service = job.service
    job.logger.info("resume vm {}".format(service.name))
    node = get_node(job)
    kvm = get_domain(job)
    if kvm:
        node.client.kvm.resume(kvm['uuid'])
        service.model.data.status = 'running'
        service.saveAll()


def shutdown(job):
    import time
    service = job.service
    job.logger.info("shutdown vm {}".format(service.name))
    node = get_node(job)
    kvm = get_domain(job)
    if kvm:
        service.model.data.status = 'halting'
        node.client.kvm.shutdown(kvm['uuid'])
        # wait for max 60 seconds for vm to be shutdown
        start = time.time()
        while start + 60 > time.time():
            kvm = get_domain(job)
            if kvm:
                time.sleep(3)
            else:
                service.model.data.status = 'halted'
                break
        else:
            service.model.data.status = 'error'
            raise j.exceptions.RuntimeError("Failed to shutdown vm {}".format(service.name))
        if service.model.data.status == 'halted':
            cleanupzerodisk(job)
    else:
        service.model.data.status = 'halted'
        cleanupzerodisk(job)

    service.saveAll()


def ssh_deamon_running(node, port):
    for nodeport in node.client.info.port():
        if nodeport['network'] == 'tcp' and nodeport['port'] == port:
            return True
    return False


def start_migartion_channel(job, old_service, new_service):
    import time
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    old_node = Node.from_ays(old_service, job.context['token'])
    node = Node.from_ays(new_service, job.context['token'])
    service = job.service
    command = "/usr/sbin/sshd -D -f {config}"
    res = None
    port = None

    try:
        # Get free ports on node to use for ssh
        freeports_node, _ = get_baseports(job, node, 4000, 1, 'migrationtcp')

        # testing should br changed to not
        if not freeports_node:
            raise j.exceptions.RuntimeError('No free port availble on taget node for migration')

        port = freeports_node[0]
        tcp_service = service.aysrepo.serviceGet(instance='migrationtcp_%s_%s' % (node.name, freeports_node[0]), role='tcp')
        tcp_service.executeAction('install', context=job.context)
        service.consume(tcp_service)
        service.saveAll()
        ssh_config = "/tmp/ssh.config_%s_%s" % (service.name, port)

        # check channel does not exist
        if node.client.filesystem.exists(ssh_config):
            node.client.filesystem.remove(ssh_config)

        # start ssh server on new node for this migration
        node.upload_content(ssh_config, "Port %s" % port)
        res = node.client.system(command.format(config=ssh_config))
        if not res.running:
            raise j.exceptions.RuntimeError("Failed to run sshd instance to migrate vm from%s_%s" % (old_node.name,
                                                                                                     node.name))
        # wait for max 5 seconds until the ssh deamon starts listening
        start = time.time()
        while time.time() < start + 5:
            if ssh_deamon_running(node, port):
                break
        else:
            raise j.exceptions.RuntimeError("sshd instance failed to start listening within 5 seconds"
                                            + " to migrate vm from%s_%s" % (old_node.name, node.name))

        # add host names addr to each node
        file_discriptor = node.client.filesystem.open("/etc/hosts", mode='a')
        host_name = old_node.client.info.os().get("hostname")
        node.client.filesystem.write(file_discriptor,
                                     str.encode("\n{hostname}    {addr}\n".format(hostname=old_node.addr,
                                                                                  addr=host_name)))
        node.client.filesystem.close(file_discriptor)

        file_discriptor = old_node.client.filesystem.open("/etc/hosts", mode='a')
        host_name = node.client.info.os().get("hostname")
        old_node.client.filesystem.write(file_discriptor,
                                         str.encode("\n{hostname}    {addr}\n".format(hostname=node.addr,
                                                                                      addr=host_name)))
        node.client.filesystem.close(file_discriptor)

        # Move keys from old_node to node authorized_keys
        if not old_node.client.filesystem.exists("/root/.ssh/id_rsa.pub"):
            old_node.client.bash("ssh-keygen -f /root/.ssh/id_rsa -t rsa -N ''").get()

        file_discriptor = old_node.client.filesystem.open("/root/.ssh/id_rsa.pub", mode='r')
        pub_key = old_node.client.filesystem.read(file_discriptor)
        old_node.client.filesystem.close(file_discriptor)
        file_discriptor = node.client.filesystem.open("/root/.ssh/authorized_keys", mode='a')
        node.client.filesystem.write(file_discriptor, pub_key)
        old_node.client.filesystem.close(file_discriptor)

        # write the ssh identy into the known hosts of old node if it doesnt exist
        ssh_identity = old_node.client.system('ssh-keyscan -p %s %s' % (port, node.addr)).get().stdout
        if not ssh_identity:
            raise j.exceptions.RuntimeError('could not get the ssh identity')
        exists = old_node.client.filesystem.exists("/root/.ssh/known_hosts")
        if exists:
            known_hosts = old_node.download_content("/root/.ssh/known_hosts")
        if not exists or ssh_identity not in known_hosts:
            file_discripter = old_node.client.filesystem.open("/root/.ssh/known_hosts", mode='a')
            old_node.client.filesystem.write(file_discripter, str.encode(ssh_identity))
            old_node.client.filesystem.close(file_discripter)

        return str(port), res.id
    except Exception as e:
        service.model.changeParent(old_service)
        service.model.data.node = old_service.name
        service.model.data.status = 'running'
        service.saveAll()
        old_service.saveAll()
        new_service.saveAll()
        if res:
            node.client.job.kill(res.id)
        if node.client.filesystem.exists('/tmp/ssh.config_%s_%s' % (service.name, port)):
            node.client.filesystem.remove('/tmp/ssh.config_%s_%s' % (service.name, port))
        if not port:
            raise e
        tcp_name = "migrationtcp_%s_%s" % (new_service.name, str(port))
        tcp_services = service.aysrepo.servicesFind(role='tcp', name=tcp_name)
        if tcp_services:
            tcp_service = tcp_services[0]
            tcp_service.executeAction("drop", context=job.context)
            tcp_service.delete()

        raise e


def get_baseports(job, node, baseport, nrports, name=None):
    """
    look for nrports free ports on node, starting from baseport
    it retuns 2 lists,
    - list of selected port, [int]
    - list of tcp ays services, [Service]
    """
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
            port = node.freeports(baseport=baseport, nrports=1)
            if not port:
                return None
            baseport = port[0]

            args = {
                'node': node.name,
                'port': baseport,
            }
            tcp = 'tcp_{}_{}'.format(node.name, baseport)
            if name:
                tcp = '{}_{}_{}'.format(name, node.name, baseport)
            tcpservices.append(tcpactor.serviceCreate(instance=tcp, args=args))
            freeports.append(baseport)
            if len(freeports) >= nrports:
                return freeports, tcpservices
        baseport += 1


def save_config(job, vdisks=None):
    import yaml
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    config = {"vdisks": list(service.model.data.vdisks)}
    yamlconfig = yaml.safe_dump(config, default_flow_style=False)

    etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
    etcd = EtcdCluster.from_ays(etcd_cluster, job.context['token'])

    etcd.put(key="%s:nbdserver:conf:vdisks" % service.name, value=yamlconfig)


def migrate(job):
    import time
    import random
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service

    service.model.data.status = 'migrating'

    node = service.model.data.node
    if not node:
        raise j.exceptions.Input("migrate action expect to have the destination node in the argument")

    # define node services
    target_node = service.aysrepo.serviceGet('node', node)
    target_node_sal = Node.from_ays(target_node, job.context['token'])
    
    old_node = service.parent
    job.logger.info("start migration of vm {} from {} to {}".format(service.name, service.parent.name, target_node.name))

    # start migration channel to copy keys and start ssh deamon
    ssh_port, job_id = start_migartion_channel(job, old_node, target_node)
    
    #start tlog server on target node
    services = [node for node in service.aysrepo.servicesFind(role="node") if node.model.data.status != "halted"]
    if len(services) < 2:
        raise RuntimeError("live migration is not possible if the enviroment has less then two nodes running")

    services.remove(old_node) # source node

    if len(services) == 1:
        # if we only have one node available, no other choice to deploy on the same node as the vm
        tlog_target_node = services[0]
    else:
        services.remove(target_node) # make sure we don't deploy on the same node as the vm
        tlog_target_node = random.choice(services)

    job.logger.info("selected node for tlog server for vm migration of vm %s: %s", service, tlog_target_node)
    tlog_container_service = create_zerodisk_container_service(job, tlog_target_node)
    tlog_container = Container.from_ays(tlog_container_service, job.context['token'], logger=service.logger)
    # make sure container is up
    if not tlog_container.is_running():
        tlog_container.executeAction('start', context=job.context)

    # find some fee ports for the tlog servers on the target node
    ports, tcp_services = get_baseports(job, tlog_container.node, 11211, 2)
    # open the ports
    for tcp_service in tcp_services:
        tcp_service.executeAction('install', context=job.context)

    # Create tlogserver service
    bind = "%s:%s" % (tlog_container.node.storageAddr, ports[0])
    waitListenBind = "%s:%s" % (tlog_container.node.storageAddr, ports[1])
    tlogserver_service = create_service(service, tlog_container_service, role='tlogserver', bind=bind, waitListenBind=waitListenBind, acceptAddress=target_node_sal.storageAddr)
    tlogserver_service.consume(tcp_services[0])
    tlogserver_service.consume(tcp_services[1])

    # destination tlogserver consume source tlog server, so he can synchronise with it during migration
    if 'tlogserver' in service.producers and len(service.producers['tlogserver']) > 0:
        source_tlogserver_service = service.producers['tlogserver'][0]
        tlogserver_service.consume(source_tlogserver_service)
    job.logger.info("creates tlog server on {} for migration of vm {}".format(tlog_target_node, service.name))
    service.consume(tlogserver_service)

    # make sure the tlogserver is started
    tlogserver_service.executeAction('start', context=job.context)

    # start new nbdserver on target node
    nbd_container = create_zerodisk_container_service(job, target_node)
    job.logger.info("start nbd server for migration of vm {}".format(service.name))
    nbdserver = create_service(service, nbd_container)
    nbd_actor = service.aysrepo.actorGet('nbdserver')
    args = {
        'container': nbd_container.name,
    }
    nbdserver = nbd_actor.serviceCreate(instance='nbdserver_%s_%s' % (service.name, target_node.name), args=args)

    nbdserver.consume(nbd_container)
    nbdserver.consume(tlogserver_service)

    service.consume(nbdserver)
    service.consume(nbd_container)
    target_node_client = Node.from_ays(target_node, job.context['token']).client
    node_client = Node.from_ays(service.parent, job.context['token']).client

    # change parent service to new node and save
    service.model.changeParent(target_node)
    target_node.saveAll()
    old_node.saveAll()
    service.saveAll()

    # start nbds
    medias = _start_nbd(job, nbdserver.name)

    # run the migrate command
    for vm in node_client.kvm.list():
        if vm["name"] == service.name:
            uuid = vm["uuid"]
            _, nics = format_media_nics(job, medias)
            target_node_client.kvm.prepare_migration_target(
                uuid=uuid,
                nics=nics,
            )
            try:
                node_client.kvm.migrate(uuid, "qemu+ssh://%s:%s/system" % (target_node.model.data.redisAddr, ssh_port))
                break
            except Exception as e:
                service.model.data.node = old_node.name
                service.model.changeParent(old_node)
                service.saveAll()
                raise e

    # open vnc port
    node = Node.from_ays(target_node, job.context['token'])
    start = time.time()
    while start + 15 > time.time():
        kvm = get_domain(job)
        if kvm:
            service.model.data.vnc = kvm['vnc']
            if kvm['vnc'] != -1:
                if node.client.nft.rule_exists(kvm['vnc']):
                    break
                node.client.nft.open_port(kvm['vnc'])
            break
        else:
            time.sleep(3)
    else:
        service.model.data.status = 'error'
        raise j.exceptions.RuntimeError("Failed to migrate vm {}".format(service.name))

    service.model.data.status = 'running'

    # cleanup to remove ssh job and config file
    node.client.job.kill(job_id)
    node.client.filesystem.remove("/tmp/ssh.config_%s_%s" % (service.name, ssh_port))
    tcp_name = "migrationtcp_%s_%s" % (node.name, ssh_port)
    tcp_service = service.aysrepo.serviceGet(role='tcp', instance=tcp_name)
    tcp_service.executeAction("drop", context=job.context)
    tcp_service.delete()
    service.saveAll()


def _remove_duplicates(col):
    try:
        return [dict(t) for t in set([tuple(element.items()) for element in col])]
    except AttributeError:
        return [dict(t) for t in set([tuple(element.to_dict().items()) for element in col])]


def _diff(col1, col2):
    col1 = _remove_duplicates(col1)
    col2 = _remove_duplicates(col2)
    return [elem for elem in col1 if elem not in col2]


def updateDisks(job, client, args):
    if args.get('disks') is None:
        return
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    uuid = None
    if service.model.data.status == 'running':
        domain = get_domain(job)
        if domain:
            uuid = domain['uuid']
    # Get new and old disks
    new_disks = _diff(args['disks'], service.model.data.disks)
    old_disks = _diff(service.model.data.disks, args['disks'])

    # Do nothing if no disk change
    if new_disks == [] and old_disks == []:
        return

    # Set model to new data
    service.model.data.disks = args['disks']
    vdisk_container_service = create_zerodisk_container_service(job, service.parent)
    container = Container.from_ays(vdisk_container_service, job.context['token'], logger=service.logger)

    # Detatching and Cleaning old disks
    if old_disks != []:
        nbdserver = service.producers.get('nbdserver', [])[0]
        for old_disk in old_disks:
            url = _nbd_url(job, container, nbdserver, old_disk['vdiskid'])
            if uuid:
                client.client.kvm.detach_disk(uuid, {'url': url})
            nbdserver.executeAction('install', context=job.context)

    # Attaching new disks
    if new_disks != []:
        _init_zerodisk_services(job, vdisk_container_service)
        for disk in new_disks:
            diskservice = service.aysrepo.serviceGet('vdisk', disk['vdiskid'])
            service.consume(diskservice)
        service.saveAll()
        _start_nbd(job)
        nbdserver = service.producers.get('nbdserver', [])[0]
        for disk in new_disks:
            media = {'url': _nbd_url(job, container, nbdserver, disk['vdiskid'])}
            if disk['maxIOps']:
                media['iotune'] = {'totaliopssec': disk['maxIOps'],
                                   'totaliopssecset': True}
            if uuid:
                client.client.kvm.attach_disk(uuid, media)
    service.saveAll()


def updateNics(job, client, args):
    if args.get('nics') is None:
        return
    service = job.service
    if service.model.data.status == 'halted':
        service.model.data.nics = args['nics']
        service.saveAll()
        return

    uuid = get_domain(job)['uuid']

    # Get new and old disks
    new_nics = _diff(args['nics'], service.model.data.nics)
    old_nics = _diff(service.model.data.nics, args['nics'])
    # Do nothing if no nic change
    if new_nics == [] and old_nics == []:
        return

    # Add new nics
    for nic in new_nics:
        if nic not in service.model.data.nics:
            client.client.kvm.add_nic(uuid=uuid,
                                      type=nic['type'],
                                      id=nic['id'] or None,
                                      hwaddr=nic['macaddress'] or None)

    # Remove old nics
    for nic in old_nics:
        client.client.kvm.remove_nic(uuid=uuid,
                                     type=nic['type'],
                                     id=nic['id'] or None,
                                     hwaddr=nic['macaddress'] or None)

    service.model.data.nics = args['nics']
    service.saveAll()


def monitor(job):
    pass
    # raise NotADirectoryError()


def update_data(job, args):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service

    # mean we want to migrate vm from a node to another
    if 'node' in args and args['node'] != service.model.data.node:
        old_node = service.model.data.node
        container_name = 'vdisks_{}_{}'.format(service.name, old_node)
        old_vdisk_container = service.aysrepo.serviceGet('container', container_name)
        old_nbd = service.aysrepo.serviceGet(role='nbdserver', instance="nbdserver_%s_%s" % (service.name, old_node))
        old_tlog_servers = old_nbd.producers['tlogserver']

        service.model.data.node = args['node']
        service.saveAll()

        if service.model.data.status == 'halted':
            # move stopped vm
            node = service.aysrepo.serviceGet('node', args['node'])
            service.model.changeParent(node)
            service.saveAll()

            old_nbd.executeAction('stop', context=job.context)
            old_nbd.delete()

            for tlog_server in old_tlog_servers:
                tlog_server.executeAction('stop', context=job.context)
                tlog_server.delete()

            start_dependent_services(job)

        elif service.model.data.status == 'running':
            # do live migration
            migrate(job)

            old_nbd.executeAction('stop', context=job.context)
            old_nbd.delete()

            for tlog_server in old_tlog_servers:
                tlog_server.executeAction('stop', context=job.context)
                tlog_server.delete()

        else:
            raise j.exceptions.RuntimeError('cannot migrate vm if status is not runnning or halted ')

        # delete old nbd services and tlog and vdisk container(this has to be before the start_nbd method)
        job.logger.info("delete old tlog container")
        for tlog_server in old_tlog_servers:
            tlog_server.parent.executeAction('stop', context=job.context)
            tlog_server.parent.delete()

        job.logger.info("delete old nbd services and vdisk container")
        old_vdisk_container.executeAction('stop', context=job.context)
        old_vdisk_container.delete()

    service.model.data.memory = args.get('memory', service.model.data.memory)
    service.model.data.cpu = args.get('cpu', service.model.data.cpu)
    service.saveAll()


def export(job):
    from zeroos.orchestrator.sal.FtpClient import FtpClient
    import hashlib
    import time
    import yaml

    service = job.service
    # url should be one of those formats
    # ftp://1.2.3.4:200
    # ftp://user@127.0.0.1:200
    # ftp://user:pass@12.30.120.200:3000
    # ftp://user:pass@12.30.120.200:3000/root/dir
    url = job.model.args.get("backupUrl", None)
    if not url:
        return

    url, filename = url.split("#", 1)

    if not url.startswith("ftp://"):
        url = "ftp://" + url

    if service.model.data.status != "halted":
        raise RuntimeError("Can not export a running vm")

    vdisks = service.model.data.vdisks

    # populate the metadata
    metadata = service.model.data.to_dict()
    metadata["cryptoKey"] = hashlib.md5(str(int(time.time() * 10**6)).encode("utf-8")).hexdigest()
    metadata["snapshotIDs"] = []

    args = {
        "url": url,
        "cryptoKey": metadata["cryptoKey"],
    }
    # TODO: optimize using futures
    metadata["vdisks"] = []
    for vdisk in vdisks:
        snapshotID = str(int(time.time() * 10**6))
        args["snapshotID"] = snapshotID
        vdisksrv = service.aysrepo.serviceGet(role='vdisk', instance=vdisk)
        vdisksrv.executeAction('export', context=job.context, args=args)
        metadata["snapshotIDs"].append(snapshotID)
        metadata["vdisks"].append({
            "blockSize": vdisksrv.model.data.blocksize,
            "type": str(vdisksrv.model.data.type),
            "size": vdisksrv.model.data.size,
            "readOnly": vdisksrv.model.data.readOnly,
        })

    # upload metadta to ftp server
    yamlconfig = yaml.safe_dump(metadata, default_flow_style=False)
    content = yamlconfig.encode('utf8')
    ftpclient = FtpClient(url)
    ftpclient.upload(content, filename)


def processChange(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        try:
            if args.get('backupUrl', None):
                export(job)
                return
            update_data(job, args)
            node = get_node(job)
            updateDisks(job, node, args)
            updateNics(job, node, args)
        except ValueError:
            job.logger.error("vm {} doesn't exist, cant update devices", service.name)
