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
    vdiskcount = int(vdiskcount / len(nodes))
    logging.info("Found %s ready nodes..." % (len(nodes)))
    nodeIDs = [node['id'] for node in nodes]
    nodeIPs = [node['ipaddress'] for node in nodes]

    deployInfo = {}
    try:
        deployInfo = deploy(api, nodeIDs, nodeIPs, resourcepoolserver, storagecluster, vdiskcount, vdisksize, vdisktype)
        test(api, deployInfo, nodeIDs, runtime)
        waitForData(api, nodeIDs, deployInfo, runtime, resultdir)
    except Exception as e:
        raise RuntimeError(e)
    finally:
        cleanUp(api, nodeIDs, deployInfo)


def waitForData(api, nodeIDs, deployInfo, runtime, resultdir):
    os.makedirs(resultdir, exist_ok=True)
    for nodeID in nodeIDs:
        start = time.time()
        while start + (runtime + 120) > time.time():
            try:
                containername = deployInfo[nodeID]["testContainer"]
                filepath = '/%s.test.json' % nodeID
                res = api.nodes.FileDownload(containername=containername,
                                             nodeid=nodeID,
                                             query_params={"path": filepath})
            except:
                time.sleep(1)
            else:
                if res.content == b'':
                    time.sleep(1)
                    continue
                file = '%s/%s.test.json' % (resultdir, nodeID)
                logging.info("Saving test data in %s ..." % file)
                with open(file, 'wb') as outfile:
                    outfile.write(res.content)
                    break


def test(api, deployInfo, nodeIDs, runtime):
    for nodeID in nodeIDs:
        containername = deployInfo[nodeID]["testContainer"]
        nbdConfig = deployInfo[nodeID]["nbdConfig"]
        filenames = nbdClientConnect(api, nodeID, containername, nbdConfig)

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
        api.nodes.StartContainerProcess(data=fioCommand, containername=containername, nodeid=nodeID)


def cleanUp(api, nodeIDs, deployInfo):
    logging.info("Cleaning up...")

    for nodeID in nodeIDs:
        if deployInfo.get(nodeID, None):
            nbdConfig = deployInfo[nodeID]["nbdConfig"]
            nbdContainer = deployInfo[nodeID]["nbdContainer"]
            testContainer = deployInfo[nodeID]["testContainer"]

            for vdisk in nbdConfig:
                deleteDiskCommand = {
                    'name': '/bin/g8stor',
                    'pwd': '',
                    'args': ['delete', 'deduped', vdisk['vdiskID'], " ".join(vdisk["datastorage"])],
                }
                api.nodes.StartContainerProcess(data=deleteDiskCommand, containername=nbdContainer, nodeid=nodeID)
                deleteDiskCommand = {
                    'name': '/bin/g8stor',
                    'pwd': '',
                    'args': ['delete', 'deduped', vdisk['vdiskID'], " ".join(vdisk["metadatastorage"])],
                }
                api.nodes.StartContainerProcess(data=deleteDiskCommand, containername=nbdContainer, nodeid=nodeID)

            api.nodes.DeleteContainer(nbdContainer, nodeID)
            api.nodes.DeleteContainer(testContainer, nodeID)


def deploy(api, nodeIDs, nodeIPs, resourcepoolserver, storagecluster, vdiskcount, vdisksize, vdisktype):
    deployInfo = {}
    for idx, nodeID in enumerate(nodeIDs):
        # Create filesystem to be shared amongst fio and nbd server contianers
        fss = _create_fss(resourcepoolserver, api, nodeID)

        # Create block device container and start nbd
        nbdContainer = "nbd_{}".format(str(time.time()).replace('.', ''))
        nbdFlist = "https://hub.gig.tech/gig-official-apps/blockstor-master.flist"
        createContainer(resourcepoolserver, api, nodeID, [fss], nbdFlist, nbdContainer)
        nbdConfig = startNbd(api, nodeID, storagecluster, fss, nbdContainer, vdiskcount, vdisksize, vdisktype)

        # Create and setup the test container
        testContainer = "bptest_{}".format(str(time.time()).replace('.', ''))
        fioFlist = "https://hub.gig.tech/gig-official-apps/performance-test.flist"
        createContainer(resourcepoolserver, api, nodeID, [fss], fioFlist, testContainer)
        # Load nbd kernel module
        nodeClient = g8core.Client(nodeIPs[idx])
        nodeClient.bash("modprobe nbd").get()

        deployInfo[nodeID] = {
                "nbdContainer": nbdContainer,
                "testContainer": testContainer,
                "nbdConfig": nbdConfig,
        }
    return deployInfo


def waitProcess(cl, command, jobid, nodeID, containername, state="SUCCESS"):
    res = cl.nodes.GetContainerJob(jobid, containername, nodeID).json()
    start = time.time()
    while start + 10 > time.time():
        if res["state"] == state:
            return True
        elif res["state"] == "ERROR":
            logging.error("Command %s failed to execute successfully. %s" % (command, res["stderr"]))
            break
        else:
            time.sleep(0.5)
            res = cl.nodes.GetContainerJob(jobid, containername, nodeID).json()


def nbdClientConnect(api, nodeID, containername, nbdConfig):
    filenames = ''
    for idx, val in enumerate(nbdConfig):
        nbdDisk = '/dev/nbd%s' % idx
        nbdClientCommand = {
            'name': '/bin/nbd-client',
            'pwd': '',
            'args': ['-N', val['vdiskID'], '-u', val['socketpath'], nbdDisk, '-b', '4096'],
        }
        res = api.nodes.StartContainerProcess(data=nbdClientCommand, containername=containername, nodeid=nodeID)
        jobid = res.headers["Location"].split("/")[-1]
        waitProcess(api, nbdClientCommand, jobid, nodeID, containername)
        filenames = nbdDisk if filenames == '' else '%s:%s' % (filenames, nbdDisk)
    return filenames


def createContainer(resourcepoolserver, cl, nodeID, fs, flist, hostname):
    container = resourcepool.CreateContainer.create(filesystems=fs,
                                                    flist=flist,
                                                    hostNetworking=True,
                                                    hostname=hostname,
                                                    initProcesses=[],
                                                    nics=[],
                                                    ports=[],
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
        if res['status'] == 'running':
            break
        else:
            time.sleep(1)
            res = cl.nodes.GetContainer(hostname, nodeID).json()


def startNbd(cl, nodeID, storagecluster, fs, containername, vdiskCount, vdiskSize, vdiskType):
    # Start nbd servers
    nbdConfig = []
    res = cl.storageclusters.GetClusterInfo(storagecluster).json()
    datastorages = []
    metadatastorage = ''

    clusterconfig = {
        'dataStorage': [],
    }
    for storage in res.get('dataStorage', []):
        datastorages.append("%s:%s" % (storage['ip'], storage['port']))
        clusterconfig['dataStorage'].append({"address": "%s:%s" % (storage['ip'], storage['port'])})

    for storage in res.get('metadataStorage', []):
        metadatastorage = "%s:%s" % (storage['ip'], storage['port'])
        clusterconfig['metadataStorage'] = {"address": "%s:%s" % (storage['ip'], storage['port'])}

    for i in range(vdiskCount):
        # Run nbd
        fs = fs.replace(':', os.sep)
        socketpath = '/fs/{}/server.socket.{}{}'.format(fs, containername, i)
        configpath = "/{}{}.config".format(containername, i)

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
        cl.nodes.StartContainerProcess(data=nbdCommand,
                                       containername=containername,
                                       nodeid=nodeID)
        logging.info("Starting nbdserver on node: %s", nodeID)
        nbdConfig.append({
            "socketpath": socketpath,
            "vdiskID": vdiskID,
            "datastorage": datastorages,
            "metadatastorage": metadatastorage,
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
