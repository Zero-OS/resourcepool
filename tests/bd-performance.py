import os

import json
import click
import logging
import time
import yaml

import g8core
from g8os import resourcepool

os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--resourcepoolserver', required=True, help='Resourcepool api server endpoint. Eg http://192.168.193.212:8080')
@click.option('--storagecluster', required=True, help='Name of the storage cluster in which the vdisks need to be created')
@click.option('--vdiskCount', required=True, type=int, help='Number of vdisks that need to be created')
@click.option('--vdiskSize', required=True, type=int, help='Size of disks in GB')
@click.option('--runtime', required=True, type=int, help='Time fio should be run')
@click.option('--vdiskType', required=True, help='Type of disk, should be: boot, db, cache, tmp')
@click.option('--resultDir', required=True, help='Results directory path')
def test_fio_nbd(resourcepoolserver, storagecluster, vdiskcount, vdisksize, runtime, vdisktype, resultdir):
    """Creates a storagecluster on all the nodes in the resourcepool"""
    api = resourcepool.Client(resourcepoolserver).api
    logging.info("Discovering nodes in the cluster ...")
    nodes = api.nodes.ListNodes().json()
    logging.info("Found %s ready nodes..." % (len(nodes)))
    nodeInfo = [(node['id'], node['ipaddress']) for node in nodes]

    # Creating ndb container
    for idx, node in enumerate(nodeInfo):
        containers = []
        nodeID = node[0]
        nodeIP = node[1]

        # Create filesystem to be shared amongst fio and nbd server contianers
        fss = _create_fss(resourcepoolserver, api, nodeID)

        # Create block device container and start nbd
        nbdContainer = "nbd_{}".format(str(time.time()).replace('.', ''))
        containers.append(nbdContainer)
        nbdFlist = "https://hub.gig.tech/gig-official-apps/blockstor-master.flist"
        createContainer(resourcepoolserver, api, nodeID, [fss], nbdFlist, nbdContainer)
        nbdConfig = startNbd(api, nodeID, storagecluster, fss, nbdContainer, vdiskcount, vdisksize, vdisktype)

        # Create and setup the test container
        fioFlist = "https://hub.gig.tech/gig-official-apps/performance-test.flist"
        createContainer(resourcepoolserver, api, nodeID, [fss], fioFlist, "bptest")
        containers.append("bptest")
        # Load nbd kernel module
        nodeClient = g8core.Client(nodeIP)
        nodeClient.bash("modprobe nbd").get()

        filenames = nbdClientConnect(api, nodeID, "bptest", nbdConfig)
        fioCommand = {
            'name': '/bin/fio',
            'pwd': '',
            'args': ['--iodepth=4',
                     '--ioengine=libaio',
                     '--size=1000M',
                     '--readwrite=randrw',
                     '--rwmixwrite=80',
                     '--filename=%s' % filenames,
                     '--runtime=%s' % runtime,
                     '--output=%s.test.json' % nodeID,
                     '--numjobs=1',
                     '--name=test1',
                     '--output-format=json'],
        }
        api.nodes.StartContainerProcess(data=fioCommand, containername="bptest", nodeid=nodeID)

        start = time.time()
        while start + (runtime * 2) > time.time():
            try:
                res = api.nodes.FileDownload(containername="bptest",
                                             nodeid=nodeID,
                                             query_params={"path": '/%s.test.json' % nodeID}).json()
                with open('%s/%s.test.json' % (resultdir, nodeID), 'w') as outfile:
                    json.dump(res, outfile)
                break
            except:
                time.sleep(1)
        cleaningUp(api, nodeID, containers)


def cleaningUp(cl, nodeID, containernames):
    for name in containernames:
        cl.nodes.DeleteContainer(name, nodeID)


def nbdClientConnect(cl, nodeID, containername, nbdConfig):
    filenames = ''
    for idx, val in enumerate(nbdConfig):
        nbdDisk = '/dev/nbd%s' % idx
        nbdClientCommand = {
            'name': '/bin/nbd-client',
            'pwd': '',
            'args': ['-N', val['vdiskID'], '-u', val['socketpath'], nbdDisk, '-b', '4096'],
        }
        cl.nodes.StartContainerProcess(data=nbdClientCommand, containername="bptest", nodeid=nodeID)
        filenames = nbdDisk if filenames == '' else '%s:%s' % (filenames, nbdDisk)
    return filenames


def createContainer(resourcepoolserver, cl, nodeID, fs, flist, hostname):
    container = resourcepool.Container.create(filesystems=fs,
                                              flist=flist,
                                              hostNetworking=True,
                                              hostname=hostname,
                                              initprocesses=[],
                                              nics=[],
                                              ports=[],
                                              status=resourcepool.EnumContainerStatus.halted,
                                              storage='',
                                              name=hostname)

    req = json.dumps(container.as_dict(), indent=4)

    link = "POST /nodes/{nodeid}/containers".format(nodeid=nodeID)
    logging.info("Sending the following request to the /containers api:\n{}\n\n{}".format(link, req))
    res = cl.nodes.CreateContainer(nodeid=nodeID, data=container)
    logging.info(
        "Creating new container...\n You can follow here: %s%s" % (resourcepoolserver, res.headers['Location']))

    # wait for container to be running
    res = cl.nodes.GetContainer(hostname, nodeID).json()
    start = time.time()
    while start + 60 > time.time():
        time.sleep(10)
        if res['status'] == 'running':
            break
        else:
            res = cl.nodes.GetContainer(hostname, nodeID).json()


def startNbd(cl, nodeID, storagecluster, fs, containername, vdiskCount, vdiskSize, vdiskType):
    # Start nbd servers
    nbdConfig = []
    for i in range(vdiskCount):
        # Run nbd
        fs = fs.replace(':', os.sep)
        socketpath = '/fs/{}/server.socket.{}{}'.format(fs, containername, i)
        configpath = "/{}{}.config".format(containername, i)

        clusterconfig = {
            'dataStorage': [],
        }

        res = cl.storageclusters.GetClusterInfo(storagecluster).json()
        for storage in res.get('dataStorage', []):
            clusterconfig['dataStorage'].append("%s:%s" % (storage['ip'], storage['port']))

        for storage in res.get('metadataStorage', []):
            clusterconfig['metadataStorage'] = "%s:%s" % (storage['ip'], storage['port'])

        vdiskID = "testvdisk_{}".format(str(time.time()).replace('.', ''))
        vdiskconfig = {
            'blocksize': 4096,
            'id': vdiskID,
            'readOnly': False,
            'size': vdiskSize,
            'storageCluster': storagecluster,
            'type': vdiskType
        }
        config = {
            'storageClusters': {storagecluster: clusterconfig},
            'vdisks': {vdiskID: vdiskconfig}
        }

        yamlconfig = yaml.safe_dump(config, default_flow_style=False)
        data = {"file": (yamlconfig)}
        time.sleep(1)
        cl.nodes.FileUpload(containername=containername,
                            nodeid=nodeID,
                            data=data,
                            query_params={"path": configpath},
                            content_type="multipart/form-data")

        nbdCommand = {
            'name': '/bin/nbdserver',
            'pwd': '',
            'args': ['-protocol=unix', '-address=%s' % socketpath, '-config=%s' % configpath]
        }
        cl.nodes.StartContainerProcess(data=nbdCommand,
                                       containername=containername,
                                       nodeid=nodeID)
        nbdConfig.append({
            "socketpath": socketpath,
            "vdiskID": vdiskID,
        })

    return nbdConfig


def _create_fss(resourcepoolserver, cl, nodeID):
    pool = "{}_fscache".format(nodeID)
    fs_id = "fs_{}".format(str(time.time()).replace('.', ''))
    fs = resourcepool.FilesystemCreate.create(name=fs_id,
                                              quota=0,
                                              readOnly=False)

    req = json.dumps(fs.as_dict(), indent=4)

    link = "POST /nodes/{nodeid}/storagepools/{pool}/filesystems".format(nodeid=nodeID, pool=pool)
    logging.info("Sending the following request to the /filesystem api:\n{}\n\n{}".format(link, req))
    res = cl.nodes.CreateFilesystem(nodeid=nodeID, storagepoolname=pool, data=fs)

    logging.info(
        "Creating new filesystem...\n You can follow here: %s%s" % (resourcepoolserver, res.headers['Location']))
    return "{}:{}".format(pool, fs_id)


if __name__ == "__main__":
    test_fio_nbd()
