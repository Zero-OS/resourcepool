import os

import json
import click
import logging
import time
import yaml
from io import BytesIO
from zeroos.core0.client import Client as Client0
from zeroos.orchestrator import client as apiclient

os.environ['LC_ALL'] = 'C.UTF-8'
os.environ['LANG'] = 'C.UTF-8'

logging.basicConfig(level=logging.INFO)


@click.command()
@click.option('--orchestratorserver', required=True, help='0-orchestrator api server endpoint. Eg http://192.168.193.212:8080')
@click.option('--jwt', required=True, help='jwt')
@click.option('--storagecluster', required=True, help='Name of the storage cluster in which the vdisks need to be created')
@click.option('--vdiskCount', required=True, type=int, help='Number of vdisks that need to be created')
@click.option('--vdiskSize', required=True, type=int, help='Size of disks in GB')
@click.option('--runtime', required=True, type=int, help='Time fio should be run')
@click.option('--vdiskType', required=True, type=click.Choice(['boot', 'db', 'cache', 'tmp']), help='Type of disk')
@click.option('--resultDir', required=True, help='Results directory path')
@click.option('--nodeLimit', type=int, help='Limit the number of nodes')
def test_fio_nbd(orchestratorserver, jwt, storagecluster, vdiskcount, vdisksize, runtime, vdisktype, resultdir, nodelimit):
    """Creates a storagecluster on all the nodes in the resourcepool"""
    api = apiclient.APIClient(orchestratorserver)
    api.set_auth_header("Bearer %s" % jwt)
    logging.info("Discovering nodes in the cluster ...")
    nodes = api.nodes.ListNodes().json()
    nodes = [node for node in nodes if node["status"] == "running"]

    nodelimit = nodelimit if nodelimit is None or nodelimit <= len(nodes) else len(nodes)

    if nodelimit is not None:
        if vdiskcount < nodelimit:
            raise ValueError("Vdisk count should be at least the same as number of nodes")
    elif vdiskcount < len(nodes):
        raise ValueError("Vdisk count should be at least the same as number of nodes")

    vdiskcount = int(vdiskcount / len(nodes)) if nodelimit is None else int(vdiskcount / nodelimit)

    logging.info("Found %s ready nodes..." % (len(nodes)))
    nodeIDs = [node['id'] for node in nodes]
    nodeIPs = [node['ipaddress'] for node in nodes]
    if nodelimit:
        nodeIDs = nodeIDs[:nodelimit]
        nodeIPs = nodeIPs[:nodelimit]

    deployInfo = {}
    try:
        deployInfo, vdisks = deploy(api, nodeIDs, nodeIPs, orchestratorserver, storagecluster, vdiskcount, vdisksize, vdisktype, jwt)
        mountVdisks(deployInfo, nodeIDs, nodeIPs, jwt)
        cycle = 0
        while runtime:
            if runtime < 3600:
                cycle_time = runtime
                runtime = 0
            else:
                cycle_time = 3600
                runtime -= 3600
            cycle += 1
            cycle_dir = os.path.join(resultdir, str(cycle))
            os.makedirs(cycle_dir, exist_ok=True)
            test(deployInfo, nodeIDs, cycle_time, nodeIPs, jwt)
            waitForData(nodeIDs, deployInfo, cycle_time, cycle_dir, nodeIPs, jwt)
    except Exception as e:
        raise RuntimeError(e)
    finally:
        cleanUp(nodeIPs, nodeIDs, deployInfo, jwt, vdisks)


def StartContainerJob(api, **kwargs):
    res = api.nodes.StartContainerJob(**kwargs)
    return res.headers["Location"].split("/")[-1]


def waitForData(nodeIDs, deployInfo, runtime, resultdir, nodeIPs, jwt):
    os.makedirs(resultdir, exist_ok=True)

    for idx, nodeID in enumerate(nodeIDs):
        nodeClient = Client0(nodeIPs[idx], password=jwt)
        start = time.time()
        while start + (runtime + 120) > time.time():
            try:
                testcontainerId = deployInfo[nodeID]["testContainer"]
                containerclient = nodeClient.container.client(testcontainerId)
                filepath = '/%s.test.json' % nodeID

                buff = BytesIO()
                containerclient.filesystem.download(filepath, buff)
            except:
                time.sleep(1)
            else:
                if buff.getvalue() == b'':
                    time.sleep(5)
                    continue
                file = '%s/%s.test.json' % (resultdir, nodeID)
                logging.info("Saving test data in %s ..." % file)
                with open(file, 'wb') as outfile:
                    outfile.write(buff.getvalue())
                    break


def mountVdisks(deployInfo, nodeIDs, nodeIPs, jwt):
    for idx, nodeID in enumerate(nodeIDs):
        nodeClient = Client0(nodeIPs[idx], password=jwt)
        testcontainerId = deployInfo[nodeID]["testContainer"]
        nbdConfig = deployInfo[nodeID]["nbdConfig"]
        deployInfo[nodeID]["nbdClientInfo"] = nbdClientConnect(nodeClient, nodeID, testcontainerId, nbdConfig)


def test(deployInfo, nodeIDs, runtime, nodeIPs,jwt ):
    for idx, nodeID in enumerate(nodeIDs):
        nodeClient = Client0(nodeIPs[idx], password=jwt)
        testcontainerId = deployInfo[nodeID]["testContainer"]
        clientInfo = deployInfo[nodeID]["nbdClientInfo"]
        filenames = clientInfo["filenames"]
        client_pids = clientInfo["client_pids"]
        deployInfo[nodeID]["filenames"] = filenames
        deployInfo[nodeID]["clientPids"] = client_pids
        fioCommand = ' /bin/fio \
                     --iodepth 16\
                     --ioengine libaio\
                     --size 100000000000M\
                     --readwrite randrw \
                     --rwmixwrite 20 \
                     --filename {filenames} \
                     --runtime {runtime} \
                     --output {nodeID}.test.json\
                     --numjobs {length} \
                     --name test1 \
                     --group_reporting \
                     --output-format=json \
                     --direct 1 \
                     '.format(filenames=filenames, runtime=runtime, nodeID=nodeID, length=len(filenames.split(":")) * 2)
        containerclient = nodeClient.container.client(testcontainerId)
        containerclient.system(fioCommand)


def cleanUp(nodeIPs, nodeIDs, deployInfo, jwt, vdisks):
    logging.info("Cleaning up...")

    for idx, nodeID in enumerate(nodeIDs):
        nodeClient = Client0(nodeIPs[idx], password=jwt)
        if deployInfo.get(nodeID, None):
            nbdConfig = deployInfo[nodeID]["nbdConfig"]
            nbdContainerId = deployInfo[nodeID]["nbdContainer"]
            nbdcontainerclient = nodeClient.container.client(nbdContainerId)
            testContainerId = deployInfo[nodeID]["testContainer"]
            testContainerclient = nodeClient.container.client(testContainerId)

            filenames = deployInfo[nodeID]["filenames"]
            client_pids = deployInfo[nodeID]["clientPids"]

            # Disconnecting nbd disks
            for idx, filename in enumerate(filenames.split(":")):
                disconnectDiskCommand = '/bin/nbd-client \
                                         -d {filename} \
                                         '.format(filename=filename)
                job = testContainerclient.bash(disconnectDiskCommand)
                job.get()
                if job.exists:
                    testContainerclient.job.kill(client_pids[idx])
            deleteDiskCommand = '/bin/zeroctl \
                                 delete \
                                 vdisks \
                                 {vdisks}\
                                 --config {configpath} \
                                '.format(vdisks=','.join(vdisks[nodeID]), configpath=nbdConfig["configpath"])

            response = nbdcontainerclient.system(deleteDiskCommand).get()
            if response.state != "SUCCESS":
                raise RuntimeError("Command %s failed to execute successfully. %s" % (deleteDiskCommand, response.stderr))
            nodeClient.container.terminate(testContainerId)
            nodeClient.container.terminate(nbdContainerId)


def deploy(api, nodeIDs, nodeIPs, orchestratorserver, storagecluster, vdiskcount, vdisksize, vdisktype, jwt):
    deployInfo = {}
    storageclusterInfo = getStorageClusterInfo(api, storagecluster)
    vdisks = {}
    for idx, nodeID in enumerate(nodeIDs):
        # Create filesystem to be shared amongst fio and nbd server contianers
        fss = _create_fss(orchestratorserver, api, nodeID)
        # Create block device container and start nbd
        nbdContainer = "nbd_{}".format(str(time.time()).replace('.', ''))
        nbdFlist = "https://hub.gig.tech/gig-official-apps/0-disk-master.flist"
        nodeClient = Client0(nodeIPs[idx], password=jwt)
        nbdcontainerId = createContainer(nodeClient, orchestratorserver, api, nodeID, fss, nbdFlist, nbdContainer)
        containerclient = nodeClient.container.client(nbdcontainerId)
        nbdConfig, vdiskIds= startNbd(containerclient=containerclient,
                             nodeID=nodeID,
                             storagecluster=storagecluster,
                             fs=fss,
                             containername=nbdContainer,
                             vdiskCount=vdiskcount,
                             vdiskSize=vdisksize,
                             vdiskType=vdisktype,
                             storageclusterInfo=storageclusterInfo)
        vdisks[nodeID] = vdiskIds
        # Create and setup the test container
        testContainer = "bptest_{}".format(str(time.time()).replace('.', ''))
        fioFlist = "https://hub.gig.tech/gig-official-apps/performance-test.flist"
        testcontainerId = createContainer(nodeClient, orchestratorserver, api, nodeID, fss, fioFlist, testContainer)

        # Load nbd kernel module
        response = nodeClient.system("modprobe nbd nbds_max=512").get()
        if response.state != "SUCCESS":
            raise ValueError("can't load nbd in node  %s" % (nodeID))
        deployInfo[nodeID] = {
            "nbdContainer": nbdcontainerId,
            "testContainer": testcontainerId,
            "nbdConfig": nbdConfig,
        }
    return deployInfo, vdisks


def getStorageClusterInfo(api, storagecluster):
    logging.info("Getting storagecluster info...")
    storageclusterInfo = api.storageclusters.GetClusterInfo(storagecluster).json()
    datastorages = []
    metadatastorage = ''

    clusterconfig = {
        'dataStorage': [],
    }
    for storage in storageclusterInfo.get('dataStorage', []):
        datastorages.append("%s:%s" % (storage['ip'], storage['port']))
        clusterconfig['dataStorage'].append({"address": "%s:%s" % (storage['ip'], storage['port'])})

    for storage in storageclusterInfo.get('metadataStorage', []):
        metadatastorage = "%s:%s" % (storage['ip'], storage['port'])
        clusterconfig['metadataStorage'] = {"address": "%s:%s" % (storage['ip'], storage['port'])}

    return {
        "clusterconfig": clusterconfig,
        "datastorage": datastorages,
        "metadatastorage": metadatastorage,
    }


def startNbd(containerclient, nodeID, storagecluster, fs, containername, vdiskCount, vdiskSize, vdiskType, storageclusterInfo):
    # Start nbd servers
    fs = fs.replace(':', os.sep)
    socketpath = '/fs/{}/server.socket.{}'.format(fs, containername)
    configpath = "/{}.config".format(containername)
    config = {
        'storageClusters': {storagecluster: storageclusterInfo["clusterconfig"]},
        'vdisks': {},
    }
    vdiskIDs = []
    for i in range(vdiskCount):
        # Run nbd

        vdiskID = "testvdisk_{}".format(str(time.time()).replace('.', ''))
        vdiskIDs.append(vdiskID)
        vdiskconfig = {
            'blockSize': 4096,
            'readOnly': False,
            'size': vdiskSize,
            'nbd': {"storageClusterID": storagecluster},
            'type': vdiskType
        }
        config['vdisks'][vdiskID] = vdiskconfig
    yamlconfig = yaml.safe_dump(config, default_flow_style=False)
    yamlconfig = yamlconfig.encode("utf8")
    ###
    bytes = BytesIO(yamlconfig)
    containerclient.filesystem.upload(configpath, bytes)
    nbdCommand = '/bin/nbdserver \
                  -protocol unix \
                  -address "{socketpath}" \
                  -config "{configpath}" \
                  '.format(socketpath=socketpath, configpath=configpath)
    nbdjob = containerclient.system(nbdCommand)
    jobId = nbdjob.id
    logging.info("Starting nbdserver on node: %s", nodeID)
    nbdConfig = {
        "socketpath": socketpath,
        "datastorage": storageclusterInfo["datastorage"],
        "metadatastorage": storageclusterInfo["metadatastorage"],
        "pid": jobId,
        "vdisks": vdiskIDs,
        "configpath": configpath,
    }

    logging.info("Waiting for 10 seconds to evaluate nbdserver processes")
    time.sleep(10)
    if not nbdjob.running:
        raise ValueError("nbd server on node %s is not in a valid state" % (nodeID))
    return nbdConfig, vdiskIDs


def createContainer(nodeClient, orchestratorserver, cl, nodeID, fs, flist, hostname):
    logging.info(
        "Creating new container %s" % (hostname))
    fss = "/fs/{}".format(fs.replace(':', os.sep))
    mntdir = "/mnt/storagepools/{}/filesystems/{}".format(fs[:fs.find(':')], fs[fs.find(':')+1:])
    mount = {mntdir: fss}
    containerId = nodeClient.container.create(root_url=flist,
                                              host_network=True,
                                              mount=mount,
                                              nics=[],
                                              port=None,
                                              hostname=hostname,
                                              privileged=True,
                                              name=hostname
                                              ).get()
    if not containerId:
        raise ValueError("can't create container %s" % (hostname))

    return containerId


def nbdClientConnect(nodeClient, nodeID, testcontainerId, nbdConfig):
    containerclient = nodeClient.container.client(testcontainerId)
    filenames = ''
    client_pids = []
    for idx, val in enumerate(nbdConfig["vdisks"]):
        nbdDisk = '/dev/nbd%s' % idx
        nbdClientCommand = '/bin/nbd-client  \
                      -N  {val} \
                      -u {nbdConfig} \
                      {nbdDisk} \
                      -b 4096 \
                      '.format(val=val, nbdConfig=nbdConfig['socketpath'], nbdDisk=nbdDisk)
        response = containerclient.system(nbdClientCommand).get()
        if response.state != "SUCCESS":
            raise RuntimeError("Command %s failed to execute successfully. %s" % (nbdClientCommand, response.stderr))
        filenames = nbdDisk if filenames == '' else '%s:%s' % (filenames, nbdDisk)
        client_pids.append(response.id)
    return {"filenames": filenames, "client_pids": client_pids}


def _create_fss(orchestratorserver, cl, nodeID):
    pool = "{}_fscache".format(nodeID)
    fs_id = "fs_{}".format(str(time.time()).replace('.', ''))
    fs = apiclient.FilesystemCreate.create(name=fs_id,
                                           quota=0,
                                           readOnly=False)

    req = json.dumps(fs.as_dict(), indent=4)

    link = "POST /nodes/{nodeid}/storagepools/{pool}/filesystems".format(nodeid=nodeID, pool=pool)
    logging.info("Sending the following request to the /filesystem api:\n{}\n\n{}".format(link, req))
    res = cl.nodes.CreateFilesystem(nodeid=nodeID, storagepoolname=pool, data=fs)

    logging.info(
        "Creating new filesystem...\n You can follow here: %s%s" % (orchestratorserver, res.headers['Location']))
    return "{}:{}".format(pool, fs_id)

if __name__ == "__main__":
    test_fio_nbd()
