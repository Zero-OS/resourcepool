from js9 import j

def install(job):
    import random
    import os
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from urllib.parse import urlparse

    service = job.service

    save_config(job)

    url = service.model.data.ftpURL.split("#")[0]
    parsed_url = urlparse(url)
    metadata = os.path.basename(parsed_url.path)
    url = parsed_url.geturl().split(metadata)[0]

    snapshotID = "default" # all images use default as snapshot ID

    clusterconfig = get_cluster_config(job)
    node = random.choice(clusterconfig["nodes"])
    container = create_from_template_container(job, node)
    try:
        find_resp = service.aysrepo.servicesFind(role="etcd_cluster")
        if len(find_resp) <= 0:
            raise j.exceptions.RuntimeError("no etcd_cluster service found")

        etcd_cluster = EtcdCluster.from_ays(find_resp[0], job.context["token"])
        cmd = "/bin/zeroctl import vdisk {vdiskid} {snapshotID} \
               --config {dialstrings} \
               --storage {ftpurl}".format(vdiskid=service.name,
                                          dialstrings=etcd_cluster.dialstrings,
                                          snapshotID=snapshotID,
                                          ftpurl=url)

        job.logger.info("import image {} from {}".format(service.name, url))
        job.logger.info(cmd)

        container_job = container.client.system(cmd, id="vdisk.import.%s" % service.name)

        try:
            container.waitOnJob(container_job)
        except Exception as e:
            strerror = e.args[0]
            raise RuntimeError("Failed to import vdisk %s: %s", (service.name, strerror))
    finally:
        container.stop()


def delete(job):
    import random
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    clusterconfig = get_cluster_config(job)
    node = random.choice(clusterconfig['nodes'])
    container = create_from_template_container(job, node)
    try:
        # delete disk on storage cluster
        find_resp = service.aysrepo.servicesFind(role="etcd_cluster")
        if len(find_resp) <= 0:
            raise j.exceptions.RuntimeError("no etcd_cluster service found")

        etcd_cluster = EtcdCluster.from_ays(find_resp[0], job.context["token"])

        cmd = '/bin/zeroctl delete vdisks {} --config {}'.format(service.name, etcd_cluster.dialstrings)

        job.logger.info("delete image {}".format(service.name))
        job.logger.info(cmd)

        result = container.client.system(cmd, id="vdisk.delete.%s" % service.name).get()
        if result.state != 'SUCCESS':
            raise j.exceptions.RuntimeError("Failed to run zeroctl delete {} {}".format(result.stdout, result.stderr))

        # remove config from etcd
        etcd = EtcdCluster.from_ays(etcd_cluster, job.context['token'])
        etcd.delete(key="%s:vdisk:conf:static" % service.name)
        etcd.delete(key="%s:vdisk:conf:storage:tlog" % service.name)
        etcd.delete(key="%s:vdisk:conf:storage:nbd" % service.name)

    finally:
        container.stop()


def save_config(job):
    import hashlib
    from urllib.parse import urlparse
    import yaml
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token
    service = job.service

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    vdiskstore = service.parent

    service = job.service

    etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
    etcd = EtcdCluster.from_ays(etcd_cluster, job.context['token'])

    # Save base config
    template = urlparse(service.model.data.templateVdisk).path.lstrip('/')
    base_config = {
        "blockSize": service.model.data.blocksize,
        "readOnly": True,
        "size": service.model.data.size,
        "type": "boot",
    }
    yamlconfig = yaml.safe_dump(base_config, default_flow_style=False)
    etcd.put(key="%s:vdisk:conf:static" % service.name, value=yamlconfig)

    # push tlog config to etcd
    vdiskType = "boot"
    objectStoragecluster = vdiskstore.model.data.objectCluster
    if objectStoragecluster:
        config = {
            "zeroStorClusterID": objectStoragecluster,
        }
        if vdiskstore.model.data.slaveCluster:
            config["slaveStorageClusterID"] = vdiskstore.model.data.slaveCluster or ""

        yamlconfig = yaml.safe_dump(config, default_flow_style=False)
        etcd.put(key="%s:vdisk:conf:storage:tlog" % service.name, value=yamlconfig)

    # push nbd config to etcd
    config = {
        "storageClusterID": vdiskstore.model.data.blockCluster,
    }
    if vdiskstore.model.data.objectCluster:
        config["tlogServerClusterID"] = "temp"
    yamlconfig = yaml.safe_dump(config, default_flow_style=False)
    etcd.put(key="%s:vdisk:conf:storage:nbd" % service.name, value=yamlconfig)


def get_cluster_config(job, type="block"):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    vdiskstore = service.parent

    cluster = vdiskstore.model.data.blockCluster if type == "block" else vdiskstore.model.data.objectCluster

    storageclusterservice = service.aysrepo.serviceGet(role='storage_cluster',
                                                       instance=cluster)
    cluster = StorageCluster.from_ays(storageclusterservice, job.context['token'])
    nodes = list(set(storageclusterservice.producers["node"]))
    return {"config": cluster.get_config(), "nodes": nodes, 'dataShards': cluster.data_shards, 'parityShards': cluster.parity_shards}


def create_from_template_container(job, parent):
    """
    if not it creates it.
    return the container service
    """
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    container_name = 'vdisk_{}_{}'.format(job.service.name, parent.name)
    node = Node.from_ays(parent, job.context['token'])
    config = get_configuration(job.service.aysrepo)
    container = Container(name=container_name,
                          flist=config.get('0-disk-flist', 'https://hub.gig.tech/gig-official-apps/0-disk-master.flist'),
                          host_network=True,
                          node=node)
    container.start()
    return container


def get_templatecluster(job):
    from urllib.parse import urlparse
    from zeroos.orchestrator.sal.Node import Node
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service

    template = urlparse(service.model.data.templateVdisk)

    if template.scheme == 'ardb' and template.netloc:
        return template.netloc

    node_srv = [node for node in service.aysrepo.servicesFind(role="node") if node.model.data.status != "halted"]
    if len(node_srv):
        node_srv = node_srv[0]
    else:
        raise RuntimeError("No running nodes found")

    node = Node.from_ays(node_srv, password=job.context['token'])
    conf = node.client.config.get()
    return urlparse(conf['globals']['storage']).netloc