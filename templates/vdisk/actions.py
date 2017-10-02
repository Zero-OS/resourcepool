from js9 import j


def input(job):
    service = job.service
    args = job.model.args
    if args.get('type') != 'boot' and args.get('imageId'):
        raise j.exceptions.Input("Only boot vdisks can have an image")
    if args.get('type') == 'boot' and not args.get('imageId'):
        raise j.exceptions.Input("imageId is a required field for boot vdisks")
    if args.get('type') == 'boot':
        images = service.aysrepo.servicesFind(name=args.get('imageId'), role='vdisk_image', parent="$vdiskstorage!$%s" % args.get('vdiskstorage'))
        if not images:
            raise j.exceptions.Input('image %s does not exist' % args.get('imageId'))


def install(job):
    import random
    from urllib.parse import urlparse
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    service.model.data.status = 'halted'
    if service.model.data.size > 2048:
        raise j.exceptions.Input("Maximum disk size is 2TB")

    # Create the vdisk in etcd
    save_config(job)

    if service.model.data.imageId:
        # Clone the image to the new vdisk
        targetconfig = get_cluster_config(job)
        target_node = random.choice(targetconfig['nodes'])
        vdiskstore = service.parent
        blockStoragecluster = vdiskstore.model.data.blockCluster
        vdiskType = service.model.data.type
        objectStoragecluster = vdiskstore.model.data.objectCluster

        volume_container = create_from_template_container(job, target_node)
        try:
            CMD = '/bin/zeroctl copy vdisk --config {etcd} {src_name} {dst_name} {tgtcluster}'

            if objectStoragecluster:
                object_st = service.aysrepo.serviceGet(role='storage_cluster', instance=objectStoragecluster)
                dataShards = object_st.model.data.dataShards
                parityShards = object_st.model.data.parityShards
                CMD += ' --data-shards %s --parity-shards %s' % (dataShards, parityShards)

            etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
            etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context['token'])
            cmd = CMD.format(etcd=etcd_cluster.dialstrings,
                             dst_name=service.name,
                             src_name=service.model.data.imageId,
                             tgtcluster=blockStoragecluster)

            job.logger.info(cmd)
            job_id = volume_container.client.system(cmd, id="vdisk.copy.%s" % service.name)

            volume_container.waitOnJob(job_id)
        finally:
            volume_container.stop()


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
        etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
        etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context['token'])
        cmd = '/bin/zeroctl delete vdisks {} --config {}'.format(service.name, etcd_cluster.dialstrings)
        job.logger.info(cmd)
        result = container.client.system(cmd, id="vdisk.delete.%s" % service.name).get()
        if result.state != 'SUCCESS':
            raise j.exceptions.RuntimeError("Failed to run zeroctl delete {} {}".format(result.stdout, result.stderr))
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
    base_config = {
        "blockSize": service.model.data.blocksize,
        "readOnly": service.model.data.readOnly,
        "size": service.model.data.size,
        "type": "cache" if service.model.data.type == "tmp" else str(service.model.data.type),
    }
    yamlconfig = yaml.safe_dump(base_config, default_flow_style=False)
    etcd.put(key="%s:vdisk:conf:static" % service.name, value=yamlconfig)

    # push tlog config to etcd
    vdiskType = service.model.data.type
    objectStoragecluster = '' if vdiskType == 'tmp'or vdiskType == 'cache' else vdiskstore.model.data.objectCluster
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
        "storageClusterID": vdiskstore.model.data.blockCluster
    }
    if vdiskstore.model.data.objectCluster:
        config["tlogServerClusterID"] = vdiskstore.model.data.objectCluster
        if vdiskstore.model.data.slaveCluster:
            config['slaveStorageClusterID'] = vdiskstore.model.data.slaveCluster

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


def start(job):
    service = job.service
    service.model.data.status = 'running'


def pause(job):
    service = job.service
    service.model.data.status = 'halted'


def get_srcstorageEngine(container, template):
    from urllib.parse import urlparse
    if template.scheme in ('', 'ardb'):
        if template.scheme == '' or template.netloc == '':
            config = container.node.client.config.get()
            return urlparse(config['globals']['storage']).netloc
        return template.netloc
    else:
        raise j.exceptions.RuntimeError("Unsupport protocol {}".format(template.scheme))


def rollback(job):
    import random
    import time
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    if 'vm' not in service.consumers:
        raise j.exceptions.Input('Can not rollback a disk that is not attached to a vm')
    service.model.data.status = 'rollingback'
    ts = job.model.args['timestamp']

    clusterconfig = get_cluster_config(job, type="object")
    node = random.choice(clusterconfig['nodes'])
    container = create_from_template_container(job, node)
    try:
        etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
        etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context['token'])
        data_shards = clusterconfig.pop('dataShards')
        parity_shards = clusterconfig.pop('parityShards')
        cmd = '/bin/zeroctl restore vdisk \
               -f {vdisk} \
               --config {dialstrings} \
               --end-timestamp {ts} \
               --data-shards {data_shards} \
               --parity-shards {parity_shards}'.format(vdisk=service.name,
                                                       dialstrings=etcd_cluster.dialstrings,
                                                       ts=ts,
                                                       data_shards=data_shards,
                                                       parity_shards=parity_shards)
        job.logger.info(cmd)

        container_job = container.client.system(cmd, id="vdisk.rollback.%s" % service.name)

        try:
            container.waitOnJob(container_job)
        except Exception as e:
            strerror = e.args[0]
            raise RuntimeError("Failed to restore vdisk %s: %s", (service.name, strerror))

        service.model.data.status = 'halted'
    finally:
        container.stop()


def export(job):
    import random
    from zeroos.orchestrator.sal.ETCD import EtcdCluster

    service = job.service

    if service.model.data.status != "halted":
        raise RuntimeError('Can not export a running vdisk')

    if 'vm' not in service.consumers:
        raise j.exceptions.Input('Can not export a disk that is not attached to a vm')
    url = job.model.args['url']
    cryptoKey = job.model.args['cryptoKey']
    snapshotID = job.model.args['snapshotID']

    clusterconfig = get_cluster_config(job)
    node = random.choice(clusterconfig["nodes"])
    container = create_from_template_container(job, node)
    try:
        etcd_cluster = service.aysrepo.servicesFind(role="etcd_cluster")[0]
        etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context["token"])
        cmd = "/bin/zeroctl export vdisk {vdiskid} {snapshotID} \
               --config {dialstrings} \
               --key {cryptoKey} \
               --storage {ftpurl}".format(vdiskid=service.name,
                                          cryptoKey=cryptoKey,
                                          dialstrings=etcd_cluster.dialstrings,
                                          snapshotID=snapshotID,
                                          ftpurl=url)
        job.logger.info(cmd)
        container_job = container.client.system(cmd, id="vdisk.export.%s" % service.name)

        try:
            container.waitOnJob(container_job)
        except Exception as e:
            strerror = e.args[0]
            raise RuntimeError("Failed to export vdisk %s: %s", (service.name, strerror))
    finally:
        container.stop()


def import_vdisk(job):
    import random
    import os
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from urllib.parse import urlparse

    service = job.service

    save_config(job)

    url = service.model.data.backupUrl.split("#")[0]
    parsed_url = urlparse(url)
    metadata = os.path.basename(parsed_url.path)
    url = parsed_url.geturl().split(metadata)[0]

    cryptoKey = service.model.data.backupUrl.split("#")[1]
    snapshotID = service.model.data.backupUrl.split("#")[2]

    clusterconfig = get_cluster_config(job)
    node = random.choice(clusterconfig["nodes"])
    container = create_from_template_container(job, node)
    try:
        etcd_cluster = service.aysrepo.servicesFind(role="etcd_cluster")[0]
        etcd_cluster = EtcdCluster.from_ays(etcd_cluster, job.context["token"])
        cmd = "/bin/zeroctl import vdisk {vdiskid} {snapshotID} \
               --config {dialstrings} \
               --key {cryptoKey} \
               --storage {ftpurl}".format(vdiskid=service.name,
                                          cryptoKey=cryptoKey,
                                          dialstrings=etcd_cluster.dialstrings,
                                          snapshotID=snapshotID,
                                          ftpurl=url)
        job.logger.info(cmd)
        container_job = container.client.system(cmd, id="vdisk.import.%s" % service.name)

        try:
            container.waitOnJob(container_job)
        except Exception as e:
            strerror = e.args[0]
            raise RuntimeError("Failed to import vdisk %s: %s", (service.name, strerror))
    finally:
        service.model.data.backupUrl = ""
        container.stop()


def resize(job):
    import yaml
    from zeroos.orchestrator.sal.ETCD import EtcdCluster
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    job.logger.info("resize vdisk {}".format(service.name))

    if 'size' not in job.model.args:
        raise j.exceptions.Input("size is not present in the arguments of the job")

    size = int(job.model.args['size'])
    if size > 2048:
        raise j.exceptions.Input("Maximun disk size is 2TB")
    if size < service.model.data.size:
        raise j.exceptions.Input("size is smaller then current size, disks can  only be grown")

    etcd_cluster = service.aysrepo.servicesFind(role='etcd_cluster')[0]
    etcd = EtcdCluster.from_ays(etcd_cluster, job.context['token'])

    base_config = {
        "blockSize": service.model.data.blocksize,
        "readOnly": service.model.data.readOnly,
        "size": service.model.data.size,
        "type": "cache" if service.model.data.type == "tmp" else str(service.model.data.type),
    }
    yamlconfig = yaml.safe_dump(base_config, default_flow_style=False)
    etcd.put(key="%s:vdisk:conf:static" % service.name, value=yamlconfig)

    service.model.data.size = size


def processChange(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        if args.get('size', None):
            j.tools.async.wrappers.sync(service.executeAction('resize', context=job.context, args={'size': args['size']}))
        if args.get('timestamp', None):
            if str(service.model.data.status) != "halted":
                raise j.exceptions.RuntimeError("Failed to rollback vdisk, vdisk must be halted to rollback")
            if str(service.model.data.type) not in ["boot", "db"]:
                raise j.exceptions.RuntimeError("Failed to rollback vdisk, vdisk must be of type boot or db")
            args['timestamp'] = args['timestamp'] * 10**9
            j.tools.async.wrappers.sync(service.executeAction('rollback', args={'timestamp': args['timestamp']}, context=job.context))
