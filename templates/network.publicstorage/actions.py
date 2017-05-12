def configure(job):
    """
    For packet.net we just rename the public interface to storage so the rest of the config deals with it
    this method will be called from the node.g8os install action.
    """
    nodeservice = job.service.aysrepo.serviceGet(role='node', instance=job.model.args['node_name'])
    node = j.sal.g8os.get_node(
        addr=nodeservice.model.data.redisAddr,
        port=nodeservice.model.data.redisPort,
        password=nodeservice.model.data.redisPassword or None
    )
    node.client.bash("""
    pubint=$(ip route | grep default | awk '{print $5}')
    ip link set dev $pubint down
    ip link set dev $pubint name backplane
    ip link set dev backplane up
    udhcpc -i backplane -s /usr/share/udhcp/simple.script -q
    """).get()
