
def bootstrap(job):
    # discover the node that send the event
    if not hasattr(job.model, 'request'):
        raise j.exceptions.RuntimeError("can't inspect http request")

    ip, _ = job.model.request.ip
    job.logger.info("reverse ardb loopup on IP: {}".format(ip))
    mac = j.sal.nettools.getMacAddressForIp(ip)

    service = job.service
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
    j.tools.async.wrappers.sync(node.executeActionJob('install'))
