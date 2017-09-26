from js9 import j


def get_stats_collector(service):
    stats_collectors_services = service.consumers.get('stats_collector')
    if stats_collectors_services:
        return stats_collectors_services[0]


def get_statsdb(service):
    statsdb_services = service.aysrepo.servicesFind(role='statsdb')
    if statsdb_services:
        return statsdb_services[0]


def input(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_configuration, get_jwt_token

    args = job.model.args
    ip = args.get('redisAddr')
    node = Node(ip, args.get('redisPort'), get_jwt_token(job.service.aysrepo))

    config = get_configuration(job.service.aysrepo)
    version = node.client.info.version()
    core0_version = config.get('0-core-version')
    core0_revision = config.get('0-core-revision')

    if (core0_version and core0_version != version['branch']) or \
            (core0_revision and core0_revision != version['revision']):
        raise RuntimeError(
            'Node with IP {} has a wrong version. Found version {}@{} and expected version {}@{} '.format(
                ip, version['branch'], version['revision'], core0_version, core0_revision))


def init(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    node = Node.from_ays(service, get_jwt_token(service.aysrepo))
    job.logger.info('create storage pool for fuse cache')
    poolname = '{}_fscache'.format(service.name)

    storagepool = node.ensure_persistance(poolname)
    storagepool.ays.create(service.aysrepo)

    statsdb_service = get_statsdb(service)
    if statsdb_service:
        stats_collector_actor = service.aysrepo.actorGet('stats_collector')
        args = {
            'node': service.name,
            'port': statsdb_service.model.data.port,
            'ip': statsdb_service.parent.model.data.redisAddr,

        }
        stats_collector_service = stats_collector_actor.serviceCreate(instance=service.name, args=args)
        stats_collector_service.consume(service)


def getAddresses(job):
    service = job.service
    networks = service.producers.get('network', [])
    networkmap = {}
    for network in networks:
        job = network.getJob('getAddresses', args={'node_name': service.name})
        networkmap[network.name] = j.tools.async.wrappers.sync(job.execute())
    return networkmap


def isConfigured(node, name):
    poolname = '{}_fscache'.format(name)
    fscache_sp = node.find_persistance(poolname)
    if fscache_sp is None:
        return False
    return bool(fscache_sp.mountpoint)


def install(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    # at each boot recreate the complete state in the system
    service = job.service
    node = Node.from_ays(service, get_jwt_token(job.service.aysrepo))
    job.logger.info('mount storage pool for fuse cache')
    poolname = '{}_fscache'.format(service.name)
    node.ensure_persistance(poolname)

    # Set host name
    node.client.system('hostname %s' % service.model.data.hostname).get()
    node.client.bash('echo %s > /etc/hostname' % service.model.data.hostname).get()

    job.logger.info('configure networks')
    for network in service.producers.get('network', []):
        job = network.getJob('configure', args={'node_name': service.name})
        j.tools.async.wrappers.sync(job.execute())

    stats_collector_service = get_stats_collector(service)
    statsdb_service = get_statsdb(service)
    if stats_collector_service and statsdb_service and statsdb_service.model.data.status == 'running':
        j.tools.async.wrappers.sync(stats_collector_service.executeAction(
            'install', context=job.context))
    node.client.bash('modprobe ipmi_si && modprobe ipmi_devintf').get()


def monitor(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.sal.healthcheck import HealthCheckObject
    from zeroos.orchestrator.configuration import get_jwt_token, get_configuration
    import redis

    service = job.service
    config = get_configuration(service.aysrepo)
    token = get_jwt_token(job.service.aysrepo)
    if service.model.actionsState['install'] != 'ok':
        return

    healthcheck_service = job.service.aysrepo.serviceGet(role='healthcheck', instance='node_%s' % service.name, die=False)
    if healthcheck_service is None:
        healthcheck_actor = service.aysrepo.actorGet('healthcheck')
        healthcheck_service = healthcheck_actor.serviceCreate(instance='node_%s' % service.name)
        service.consume(healthcheck_service)

    try:
        node = Node.from_ays(service, token, timeout=15)
        node.client.testConnectionAttempts = 0
        state = node.client.ping()
    except (RuntimeError, ConnectionError, redis.TimeoutError):
        state = False
    nodestatus = HealthCheckObject('nodestatus', 'Node Status', 'Node Status', '/nodes/{}'.format(service.name))

    if state:
        service.model.data.status = 'running'
        configured = isConfigured(node, service.name)
        if not configured:
            job = service.getJob('install', args={})
            j.tools.async.wrappers.sync(job.execute())

        job.context['token'] = token
        stats_collector_service = get_stats_collector(service)
        statsdb_service = get_statsdb(service)

        # Check if statsdb is installed on this node and start it if needed
        if (statsdb_service and str(statsdb_service.parent) == str(job.service)
                and statsdb_service.model.data.status != 'running'):
            j.tools.async.wrappers.sync(statsdb_service.executeAction(
                'start', context=job.context))

        # Check if there is a running statsdb and if so make sure stats_collector for this node is started
        if (stats_collector_service and stats_collector_service.model.data.status != 'running'
                and statsdb_service.model.data.status == 'running'):
            j.tools.async.wrappers.sync(stats_collector_service.executeAction(
                'start', context=job.context))

        # healthchecks
        nodestatus.add_message('node', 'OK', 'Node is running')
        update_healthcheck(job, healthcheck_service, node.healthcheck.openfiledescriptors())
        update_healthcheck(job, healthcheck_service, node.healthcheck.cpu_mem())
        update_healthcheck(job, healthcheck_service, node.healthcheck.rotate_logs())
        update_healthcheck(job, healthcheck_service, node.healthcheck.network_bond())
        update_healthcheck(job, healthcheck_service, node.healthcheck.interrupts())
        update_healthcheck(job, healthcheck_service, node.healthcheck.context_switch())
        update_healthcheck(job, healthcheck_service, node.healthcheck.threads())
        update_healthcheck(job, healthcheck_service, node.healthcheck.qemu_vm_logs())
        update_healthcheck(job, healthcheck_service, node.healthcheck.network_load())
        update_healthcheck(job, healthcheck_service, node.healthcheck.disk_usage())
        update_healthcheck(job, healthcheck_service, node.healthcheck.ssh_cleanup(job=job))

        flist = config.get('healthcheck-flist', 'https://hub.gig.tech/gig-official-apps/healthcheck.flist')
        with node.healthcheck.with_container(flist) as cont:
            update_healthcheck(job, healthcheck_service, node.healthcheck.node_temperature(cont))
            update_healthcheck(job, healthcheck_service, node.healthcheck.powersupply(cont))
            update_healthcheck(job, healthcheck_service, node.healthcheck.fan(cont))

        # check network stability of  node with the rest of the nodes ! TODO
    else:
        service.model.data.status = 'halted'
        nodestatus.add_message('node', 'ERROR', 'Node is halted')
    update_healthcheck(job, healthcheck_service, nodestatus.to_dict())

    service.saveAll()


def update_healthcheck(job, health_service, healthchecks):
    import time

    service = job.service

    interval = service.model.actionGet('monitor').period
    new_healthchecks = list()
    if not isinstance(healthchecks, list):
        healthchecks = [healthchecks]
    defaultresource = '/nodes/{}'.format(service.name)
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


def reboot(job):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service

    # Check if statsdb is installed on this node and stop it
    statsdb_service = get_statsdb(service)
    if statsdb_service and str(statsdb_service.parent) == str(job.service):
        j.tools.async.wrappers.sync(statsdb_service.executeAction(
            'stop', context=job.context))

    # Chceck if stats_collector is installed on this node and stop it
    stats_collector_service = get_stats_collector(service)
    if stats_collector_service and stats_collector_service.model.data.status == 'running':
        j.tools.async.wrappers.sync(stats_collector_service.executeAction(
            'stop', context=job.context))

    job.logger.info('reboot node {}'.format(service))
    node = Node.from_ays(service, job.context['token'])
    node.client.raw('core.reboot', {})


def uninstall(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    stats_collector_service = get_stats_collector(service)
    if stats_collector_service:
        j.tools.async.wrappers.sync(stats_collector_service.executeAction(
            'uninstall', context=job.context))

    statsdb_service = get_statsdb(service)
    if statsdb_service and str(statsdb_service.parent) == str(service):
        j.tools.async.wrappers.sync(statsdb_service.executeAction(
            'uninstall', context=job.context))

    bootstraps = service.aysrepo.servicesFind(actor='bootstrap.zero-os')
    if bootstraps:
        j.tools.async.wrappers.sync(bootstraps[0].getJob('delete_node', args={'node_name': service.name}).execute())


def watchdog(job):
    from zeroos.orchestrator.sal.Pubsub import Pubsub
    from zeroos.orchestrator.configuration import get_jwt_token
    from asyncio import sleep
    import asyncio
    import re
    import traceback

    service = job.service
    watched_roles = {
        'nbdserver': {
            # 'message': (re.compile('^storageengine-failure.*$')),  # TODO: Not implemented yet in 0-disk yet
            'eof': True
        },
        'tlogserver': {
            'eof': True,
        },
        'ork': {
            'level': 20,
            'instance': job.service.name,
            'service': 'node',
            'eof': False,
            'message': (re.compile('.*'),),
            'handler': 'ork_handler',
        },
        'kvm': {
            'level': 20,
            'instance': job.service.name,
            'service': 'node',
            'eof': False,
            'message': (re.compile('.*'),),
            'handler': 'vm_handler',
            'sub_id': 'events',
        },
        'cloudinit': {
            'eof': True,
        },
        'http': {
            'eof': True,
        },
        'dhcp': {
            'eof': True,
        },
        'storage_engine': {
            'eof': True,
        },
        "etcd": {
            "eof": True,
        },
        'stats_collector': {
            'eof': True,
        },
        'zerostor': {
            'eof': True,
        },
        'container': {
            "eof": True,
        },
    }

    async def callback(jobid, level, message, flag):
        if '.' not in jobid:
            return

        role, sub_id = jobid.split('.', 1)
        if (role not in watched_roles or
                watched_roles[role].get('level', level) != level
                or watched_roles[role].get('sub_id', sub_id) != sub_id):
            return

        service_role = watched_roles[role].get('service', role)
        instance = watched_roles[role].get('instance', sub_id)

        eof = flag & 0x6 != 0

        valid_message = False
        matched_messages = watched_roles[role].get('message', ())
        for msg in matched_messages:
            if msg.match(message):
                valid_message = True

        if not valid_message and not (watched_roles[role]['eof'] and eof):
            return

        srv = service.aysrepo.serviceGet(role=service_role, instance=instance, die=False)
        if srv:
            args = {'message': message, 'eof': eof, 'level': level}
            job.context['token'] = get_jwt_token(job.service.aysrepo)
            handler = watched_roles[role].get('handler', 'watchdog_handler')
            await srv.executeAction(handler, context=job.context, args=args)

    async def check_node(job):
        job.context['token'] = get_jwt_token(job.service.aysrepo)
        try:
            cl = Pubsub(service._loop, service.model.data.redisAddr, password=job.context['token'], callback=callback)
            await cl.ping()
            service.model.data.status = 'running'
        except (RuntimeError, OSError) as e:
            service.model.data.status = 'halted'

    async def streaming(job):
        # Check if the node is runing
        while service.model.actionsState['install'] != 'ok':
            await sleep(5)

        while str(service.model.data.status) != 'running':
            await sleep(5)

        # Add the looping here instead of the pubsub sal
        cl = None
        subscribed = None

        while True:
            if str(service.model.data.status) != 'running':
                await sleep(5)
                continue
            if cl is None:
                job.context['token'] = get_jwt_token(job.service.aysrepo)
                cl = Pubsub(service._loop, service.model.data.redisAddr, password=job.context['token'], callback=callback)

            try:
                if not subscribed:
                    queue = await cl.subscribe('ays.monitor')
                    subscribed = True
                await cl.global_stream(queue)
            except asyncio.TimeoutError as e:
                job.logger.error(e)
                await check_node(job)
                cl = None
                subscribed = None
            except OSError as e:
                job.logger.error(e)
                await check_node(job)
                cl = None
                subscribed = None
            except RuntimeError as e:
                job.logger.error(e)
                await check_node(job)
                cl = None
                subscribed = None
            except Exception as e:
                job.logger.error(traceback.format_exc())
                await check_node(job)
                cl = None
                subscribed = None

    return streaming(job)


def nic_shutdown(job, message):
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    service = job.service
    node = Node.from_ays(service, get_jwt_token(service.aysrepo))
    interface = message['name']

    if interface.startswith('cont'):
        container_id = interface.split('-')[0].replace('cont', '')
        for container in node.containers.list():
            if str(container.id) == container_id:
                container_service = service.aysrepo.serviceGet(role='container', instance=container.name)
                container_service.model.data.status = 'networkKilled'
                container_service.saveAll()
                return
    else:
        vms = node.client.kvm.list()
        for vm in vms:
            if interface in vm['ifctargets']:
                vm_service = service.aysrepo.serviceGet(role='vm', instance=vm['name'])
                vm_service.model.data.status = 'networkKilled'
                vm_service.saveAll()
                return

    job.logger.info('Failed to find vm/container interface matching %s' % interface)


def ork_handler(job):
    import json

    message = job.model.args.get('message')
    if not message:
        return

    message = json.loads(message)
    if message['action'] == 'NIC_SHUTDOWN':
        nic_shutdown(job, message)


def start_vm(job, vm):
    import asyncio
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    if vm.model.data.status == 'running':
        asyncio.ensure_future(vm.executeAction('start', context=job.context), loop=service._loop)


def shutdown_vm(job, vm):
    import asyncio
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    if vm.model.data.status == 'running':
        asyncio.ensure_future(vm.executeAction('shutdown', context=job.context), loop=service._loop)


def vm_handler(job):
    import json

    message = job.model.args.get('message')
    if not message:
        return

    message = json.loads(message)
    vm = job.service.aysrepo.serviceGet(role='vm', instance=message['name'])
    if not vm:
        return

    if message['event'] == 'stopped' and message['detail'] == 'failed':
        start_vm(job, vm)

    if message['event'] == 'stopped' and message['detail'] == 'shutdown':
        shutdown_vm(job, vm)
