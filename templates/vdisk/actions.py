from js9 import j


def install(job):
    import random
    from urllib.parse import urlparse
    import yaml

    service = job.service
    service.model.data.status = 'halted'

    if service.model.data.templateVdisk:
        template = urlparse(service.model.data.templateVdisk)
        targetconfig = get_storagecluster_config(service)
        target_node = random.choice(targetconfig['nodes'])
        storagecluster = service.model.data.storageCluster

        volume_container = create_from_template_container(service, target_node)
        try:
            srcardb = get_srcardb(volume_container, template)
            configpath = "/config.yml"
            disktype = "cache" if str(service.model.data.type) == "tmp" else str(service.model.data.type)
            config = {
                "storageClusters": {
                    storagecluster: targetconfig['config'],
                    "srccluster": {
                        "metadataStorage": {
                            "address": srcardb
                        },
                        "dataStorage": [
                            {"address": srcardb},
                        ],
                    },
                },
                "vdisks": {
                    template.path.lstrip('/'): {
                        "blockSize": service.model.data.blocksize,  # Random value needed only to complete the config
                        "readOnly": service.model.data.readOnly,  # Random value needed only to complete the config
                        "size": service.model.data.size,  # Random value needed only to complete the config
                        "storageCluster": "srccluster",
                        "type": disktype,
                    }
                }
            }
            yamlconfig = yaml.safe_dump(config, default_flow_style=False)
            volume_container.upload_content(configpath, yamlconfig)

            CMD = '/bin/g8stor copy vdisk {src_name} {dst_name} {tgtcluster}'
            cmd = CMD.format(dst_name=service.name, src_name=template.path.lstrip('/'), tgtcluster=storagecluster)

            print(cmd)
            result = volume_container.client.system(cmd).get()
            if result.state != 'SUCCESS':
                raise j.exceptions.RuntimeError("Failed to run g8stor copy {} {}".format(result.stdout, result.stderr))

        finally:
            volume_container.stop()


def delete(job):
    import random
    import yaml

    service = job.service
    storagecluster = service.model.data.storageCluster
    clusterconfig = get_storagecluster_config(service)
    node = random.choice(clusterconfig['nodes'])
    container = create_from_template_container(service, node)
    configpath = "/config.yaml"
    disktype = "cache" if str(service.model.data.type) == "tmp" else str(service.model.data.type)
    config = {
                "storageClusters": {
                    storagecluster: clusterconfig['config']
                },
                "vdisks": {
                    service.name: {
                        "blockSize": service.model.data.blocksize,
                        "readOnly": service.model.data.readOnly,
                        "size": service.model.data.size,
                        "storageCluster": storagecluster,
                        "type": disktype,
                    }
                }
            }
    yamlconfig = yaml.safe_dump(config, default_flow_style=False)
    container.upload_content(configpath, yamlconfig)

    cmd = '/bin/g8stor delete vdisks --config {}'.format(configpath)
    print(cmd)
    result = container.client.system(cmd).get()
    if result.state != 'SUCCESS':
        raise j.exceptions.RuntimeError("Failed to run g8stor delete {} {}".format(result.stdout, result.stderr))


def get_srcardb(container, template):
    from urllib.parse import urlparse

    if template.scheme in ('', 'ardb'):
        if template.scheme == '' or template.netloc == '':
            config = container.node.client.config.get()
            return urlparse(config['globals']['storage']).netloc
        return template.netloc
    else:
        raise j.exceptions.RuntimeError("Unsupport protocol {}".format(template.scheme))


def get_storagecluster_config(service):
    from zeroos.orchestrator.sal.StorageCluster import StorageCluster
    storagecluster = service.model.data.storageCluster
    storageclusterservice = service.aysrepo.serviceGet(role='storage_cluster',
                                                       instance=storagecluster)
    cluster = StorageCluster.from_ays(storageclusterservice)
    return {"config": cluster.get_config(), "nodes": storageclusterservice.producers["node"]}


def create_from_template_container(service, parent):
    """
    if not it creates it.
    return the container service
    """
    from zeroos.orchestrator.configuration import get_configuration
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.Node import Node

    container_name = 'vdisk_{}_{}'.format(service.name, parent.name)
    node = Node.from_ays(parent)
    config = get_configuration(service.aysrepo)
    container = Container(name=container_name,
                          flist=config.get('blockstor-flist', 'https://hub.gig.tech/gig-official-apps/blockstor-master.flist'),
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


def rollback(job):
    service = job.service
    service.model.data.status = 'rollingback'
    # TODO: rollback disk
    service.model.data.status = 'running'


def resize(job):
    service = job.service
    job.logger.info("resize vdisk {}".format(service.name))

    if 'size' not in job.model.args:
        raise j.exceptions.Input("size is not present in the arguments of the job")

    size = int(job.model.args['size'])
    if size < service.model.data.size:
        raise j.exceptions.Input("size is smaller then current size, disks can grown")

    service.model.data.size = size


def processChange(job):
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        j.tools.async.wrappers.sync(service.executeAction('resize', args={'size': args['size']}))
