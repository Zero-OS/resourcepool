import os

import json
import click
import logging
import time
import yaml
import sys
import g8core
from g8os import resourcepool

import asyncio
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('')


@click.command()
@click.option('--resourcepoolserver', required=True, help='Resourcepool api server endpoint. Eg http://192.168.193.212:8080')
@click.option('--storagecluster', required=True, help='Name of the storage cluster in which the vdisks need to be created')
@click.option('--vdiskCount', required=True, type=int, help='Number of vdisks that need to be created')
@click.option('--vdiskSize', required=True, type=int, help='Size of disks in GB')
@click.option('--runtime', required=True, type=int, help='Time fio should be run')
@click.option('--vdiskType', required=True, help='Type of disk, should be: boot, db, cache, tmp')
@click.option('--resultDir', required=True, help='Results directory path')
@click.option('--cleanup', is_flag=True, help='Remove test containers after finishing the test')
def main(resourcepoolserver, storagecluster, vdiskcount, vdisksize, runtime, vdisktype, resultdir, cleanup):
    """Creates a storagecluster on all the nodes in the resourcepool"""
    api = resourcepool.Client(resourcepoolserver).api
    LOG.info("Discovering nodes in the cluster ...")
    nodes = api.nodes.ListNodes().json()
    vdiskcount = int(vdiskcount / len(nodes))
    LOG.info("Found %s ready nodes..." % (len(nodes)))
    nodeInfo = [(node['id'], node['ipaddress']) for node in nodes]

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(fioTest(nodeInfo, resourcepoolserver, api, storagecluster, vdiskcount, vdisksize, vdisktype, runtime, resultdir, cleanup))
    finally:
        event_loop.close()


async def fioTest(nodeInfo, resourcepoolserver, api, storagecluster, vdiskcount, vdisksize, vdisktype, runtime, resultdir, cleanup):
    # Creating ndb container
    coroutines = []
    for idx, node in enumerate(nodeInfo):
        nodeID = node[0]
        nodeIP = node[1]
        coroutines.append(startTest(nodeID, nodeIP, resourcepoolserver, api, storagecluster, vdiskcount, vdisksize, vdisktype, runtime, resultdir, cleanup))
    await asyncio.wait(coroutines)


async def startTest(nodeID, nodeIP, resourcepoolserver, api, storagecluster, vdiskcount, vdisksize, vdisktype, runtime, resultdir, cleanup):
    containers = []
    # Create filesystem to be shared amongst fio and nbd server contianers
    fss = await createFss(resourcepoolserver, api, nodeID)

    # Create block device container and start nbd
    nbdContainer = "nbd_{}".format(str(time.time()).replace('.', ''))
    containers.append(nbdContainer)
    nbdFlist = "https://hub.gig.tech/gig-official-apps/blockstor-master.flist"
    await createContainer(resourcepoolserver, api, nodeID, [fss], nbdFlist, nbdContainer)
    nbdConfig = await startNbd(api, nodeID, storagecluster, fss, nbdContainer, vdiskcount, vdisksize, vdisktype)

    # Create and setup the test container
    fioFlist = "https://hub.gig.tech/gig-official-apps/performance-test.flist"
    await createContainer(resourcepoolserver, api, nodeID, [fss], fioFlist, "bptest")
    containers.append("bptest")
    # Load nbd kernel module
    nodeClient = g8core.Client(nodeIP)
    nodeClient.bash("modprobe nbd").get()

    LOG.info("Start testing block devices on node: %s ..." % nodeID)
    filenames = await nbdClientConnect(api, nodeID, "bptest", nbdConfig)
    fioCommand = {
        'name': '/bin/fio',
        'pwd': '',
        'args': ['--iodepth=4',
                 '--ioengine=libaio',
                 '--size=1000M',
                 '--readwrite=randrw',
                 '--rwmixwrite=20',
                 '--filename=%s' % filenames,
                 '--runtime=%s' % runtime,
                 '--output=%s.test.json' % nodeID,
                 '--numjobs=1',
                 '--name=test1',
                 '--output-format=json'],
    }
    api.nodes.StartContainerProcess(data=fioCommand, containername="bptest", nodeid=nodeID)

    start = time.time()
    while start + (runtime + 60) > time.time():
        try:
            res = api.nodes.FileDownload(containername="bptest", nodeid=nodeID, query_params={"path": '/%s.test.json' % nodeID})
        except:
            await asyncio.sleep(1)
        else:
            if res.content == b'':
                await asyncio.sleep(1)
                continue
            file = '%s/%s.test.json' % (resultdir, nodeID)
            LOG.info("Saving test data in %s" % file)
            with open(file, 'wb') as outfile:
                outfile.write(res.content)
                break
    if cleanup:
        await cleaningUp(api, nodeID, containers, nbdConfig)


async def cleaningUp(cl, nodeID, containernames, nbdConfig):
    LOG.info(nbdConfig)

    for name in containernames:
        if name.startswith("nbd"):
            for vdisk in nbdConfig:
                for storage in vdisk["datastorage"]:
                    deleteDiskCommand = {
                        'name': '/bin/g8stor',
                        'pwd': '',
                        'args': ['delete', 'deduped', vdisk['vdiskID'], storage],
                    }
                    cl.nodes.StartContainerProcess(data=deleteDiskCommand, containername=name, nodeid=nodeID)

                deleteDiskCommand = {
                    'name': '/bin/g8stor',
                    'pwd': '',
                    'args': ['delete', 'deduped', vdisk['vdiskID'], vdisk["metadatastorage"]],
                }
                cl.nodes.StartContainerProcess(data=deleteDiskCommand, containername=name, nodeid=nodeID)

        LOG.info("Destroing container %s of node %s", name, nodeID)
        cl.nodes.DeleteContainer(name, nodeID)


async def nbdClientConnect(cl, nodeID, containername, nbdConfig):
    filenames = ''
    for idx, val in enumerate(nbdConfig):
        nbdDisk = '/dev/nbd%s' % idx
        nbdClientCommand = {
            'name': '/bin/nbd-client',
            'pwd': '',
            'args': ['-N', val['vdiskID'], '-u', val['socketpath'], nbdDisk, '-b', '4096'],
        }
        res = cl.nodes.StartContainerProcess(data=nbdClientCommand, containername="bptest", nodeid=nodeID)
        jobid = res.headers["Location"].split("/")[-1]

        if await waitProcess(cl, nbdClientCommand, jobid, nodeID, "bptest"):
            filenames = nbdDisk if filenames == '' else '%s:%s' % (filenames, nbdDisk)
    return filenames


async def waitProcess(cl, command, jobid, nodeID, containername, state="SUCCESS"):
    res = cl.nodes.GetContainerJob(jobid, containername, nodeID).json()
    start = time.time()
    while start + 10 > time.time():
        if res["state"] == state:
            return True
        elif res["state"] == "ERROR":
            LOG.error("Command %s failed to execute successfully. %s" % (command, res["stderr"]))
            break
        else:
            await asyncio.sleep(0.5)
            res = cl.nodes.GetContainerJob(jobid, containername, nodeID).json()
    return False


async def createContainer(resourcepoolserver, cl, nodeID, fs, flist, hostname):
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
    LOG.info("Sending the following request to the /containers api:\n{}\n\n{}".format(link, req))
    res = cl.nodes.CreateContainer(nodeid=nodeID, data=container)
    LOG.info(
        "Creating new container...\n You can follow here: %s%s" % (resourcepoolserver, res.headers['Location']))

    # wait for container to be running
    res = cl.nodes.GetContainer(hostname, nodeID).json()
    start = time.time()
    while start + 60 > time.time():
        if res['status'] == 'running':
            break
        else:
            await asyncio.sleep(1)
            res = cl.nodes.GetContainer(hostname, nodeID).json()


async def startNbd(cl, nodeID, storagecluster, fs, containername, vdiskCount, vdiskSize, vdiskType):
    # Start nbd servers
    nbdConfig = []
    LOG.info("Starting NBD servers on node: %s", nodeID)
    for i in range(vdiskCount):
        # Run nbd
        fs = fs.replace(':', os.sep)
        socketpath = '/fs/{}/server.socket.{}{}'.format(fs, containername, i)
        configpath = "/{}{}.config".format(containername, i)

        clusterconfig = {
            'dataStorage': [],
        }

        res = cl.storageclusters.GetClusterInfo(storagecluster).json()
        datastorages = []
        metadatastorage = ''
        for storage in res.get('dataStorage', []):
            datastorages.append("%s:%s" % (storage['ip'], storage['port']))
            clusterconfig['dataStorage'].append({"address": "%s:%s" % (storage['ip'], storage['port'])})

        for storage in res.get('metadataStorage', []):
            metadatastorage = "%s:%s" % (storage['ip'], storage['port'])
            clusterconfig['metadataStorage'] = {"address": "%s:%s" % (storage['ip'], storage['port'])}

        vdiskID = "testvdisk_{}".format(str(time.time()).replace('.', ''))
        vdiskconfig = {
            'blockSize': 4096,
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
        res = cl.nodes.StartContainerProcess(data=nbdCommand,
                                             containername=containername,
                                             nodeid=nodeID)
        jobid = res.headers["Location"].split("/")[-1]
        await waitProcess(cl, nbdCommand, jobid, nodeID, containername, "running")

        nbdConfig.append({
            "socketpath": socketpath,
            "vdiskID": vdiskID,
            "datastorage": datastorages,
            "metadatastorage": metadatastorage,
        })

    return nbdConfig


async def createFss(resourcepoolserver, cl, nodeID):
    pool = "{}_fscache".format(nodeID)
    fs_id = "fs_{}".format(str(time.time()).replace('.', ''))
    fs = resourcepool.FilesystemCreate.create(name=fs_id,
                                              quota=0,
                                              readOnly=False)

    req = json.dumps(fs.as_dict(), indent=4)

    link = "POST /nodes/{nodeid}/storagepools/{pool}/filesystems".format(nodeid=nodeID, pool=pool)
    LOG.info("Sending the following request to the /filesystem api:\n{}\n\n{}".format(link, req))
    res = cl.nodes.CreateFilesystem(nodeid=nodeID, storagepoolname=pool, data=fs)

    LOG.info(
        "Creating new filesystem...\n You can follow here: %s%s" % (resourcepoolserver, res.headers['Location']))
    return "{}:{}".format(pool, fs_id)


if __name__ == "__main__":
    main()
