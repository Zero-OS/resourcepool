from JumpScale import j

def bootstrap(job):
    # discover the node that send the event
    if not hasattr(job.model, 'request'):
        raise j.exceptions.RuntimeError("can't inspect http request")

    ip, _ = job.model.request.ip
    job.logger.info("reverse ardb loopup on IP: {}".format(ip))
    mac = j.sal.nettools.getMacAddressForIp(ip)

    service = job.service

    try:
        job.logger.info("service for node {} already exists, updating model".format(mac))
        node = service.aysrepo.serviceGet(role='node', instance=mac)
        # mac sure the service has the correct ip in his model.
        # it could happend that a node get a new ip after a reboot
        node.model.data.redisAddr = ip
        node.model.data.status = 'running'

    except j.exceptions.NotFound:
        # create and install the node.g8os service
        node_actor = job.service.aysrepo.actorGet('node.g8os')
        networks = [n.name for n in service.producers.get('network', [])]

        node_args = {
            'id': mac,
            'status':'running',
            'networks': networks,
            'redisAddr': ip,
        }
        job.logger.info("create node.g8os service {}".format(mac))
        node = node_actor.serviceCreate(instance=mac, args=node_args)

        job.logger.info("install node.g8os service {}".format(mac))
        j.tools.async.wrappers.sync(node.executeAction('install'))
