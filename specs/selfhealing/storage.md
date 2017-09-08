# NBD server
The NBD server is connected to AYS via the logging streaming offered by zero-os. If errors occur like eg an ARDB server that is not healty anymore, the NBD server will emit error logs that will be intercepted by the node.zero-os watchdog and propagated to the particular NBD service in AYS.

# NBD server failure
When an NBD server would crash, AYS will discover that instantaneously through its long living watchdog action.
AYS then needs to restarts the NBD server and the corresponding VM.

# Tlog server failure
As we deploy multiple Tlog servers per NBD server (https://github.com/zero-os/0-Disk/issues/279), AYS just needs to restart the Tlog server when it crashed.

# SSD failure in Primary Storage Cluster
When an NBD server is unable to read or write from storage engine (ARDB server) with modulo X, it will fail over to the slave storage cluster to continue serving blocks for shard X. At the same time it will report the failure on its stderr stream (```{"type": "storageengine-failure", "data": "10.100.0.1:22005"}```) that is monitored by the long-living watchdog action of the node.zero-os service and propagated to the NBD service.

AYS will then analyze if the ARDB problem is a temporary problem, due to a reboot or restart of the ARDB server, or a permanent problem due to a disk crash to which the ARDB server is writing its blocks.

## Recovering from an outage of a storage engine (ARDB)

### Step 1: flag storage cluster to status repairing
This will prevent any creation or deletion of new vdisks.

### Step 2: notify all NBD servers that a specific storage engine is not functional
Update all impacted vdisks that a certain shard is repairing.

By means of updating the AYS model (storage_engine service) and the corresponding configuration in the etcd cluster, all NDB servers that are runnning will be notified that the storage engine is faulty (```status: offline```), and that it needs to fail over to the slave cluster for the specific shard that is offline.

Updating the AYS model needs to be done atomically, to prevent double actions, because the same problem will potentially be notified by multiple NBD servers. See https://github.com/Jumpscale/ays9/issues/38

### Step 3: analyze the problem
The storage_engine service will now analyze wether the outage of the ARDB service is temporary or final. 

### Step 4: repair the problem

#### Temporary interruption of the storage_engine
If its temporary, as soon as AYS is able get the storage_engine running again (eg, wait until the node has completed rebooting, or restarted the ARDB server after a crash) it will update the AYS model and corresponding etcd configuration and assign a status (```status: repair-tmp-outage```). This will make the running NDB servers start repairing. 

vdisks (NBD servers) that are not running will be repaired by a NBD server started on a node part of the storage network. While this NDB server is repairing, it should not be possible to start a vm on it.

If the repairing is interrupted, AYS will restart the repair by spinning up an NDB server to continue the repairing job until it is complete.

When the NDB server has completed repairing the situation, it will emit the following log line to its std-err stream ```{"type": "repair-tmp-outage-complete", "data": {"address": "10.100.0.1:22005", "vdiskid": "23"}}```, and start to serve blocks again from this storage engine. Via the node.zero-os watchdog action in AYS this problem will be propagated to the vdisk service. If all vdisks completed repairing the storage_engine service will marked as online again (```status: online```) both in the AYS model and in the etcd cluster. On top of that the storage cluster will be marked healthy again so that vdisk creation and deletion will be operational again.

#### Permanent interruption of the storage engine
If its temporary, as soon as AYS is able get the storage_engine running again (eg, wait until the node has completed rebooting, or restarted the ARDB server after a crash) it will update the AYS model and corresponding etcd configuration and assign a status (```status: repair-final-outage```). This will make the running NDB servers start repairing. 

vdisks (NBD servers) that are not running will be repaired by a NBD server started on a node part of the storage network. While this NDB server is repairing, it should not be possible to start a vm on it.

If the repairing is interrupted, AYS will restart the repair by spinning up an NDB server to continue the repairing job until it is complete.

When the NDB server has completed repairing the situation, it will emit the following log line to its std-err stream ```{"type": "repair-final-outage-complete", "data": {"address": "10.100.0.1:22005", "vdiskid": "23"}}```, and start to serve blocks again from this storage engine. Via the node.zero-os watchdog action in AYS this problem will be propagated to the vdisk service. If all vdisks completed repairing the storage_engine service will marked permenantly offline (```status: rip```) both in the AYS model and in the etcd cluster. On top of that the storage cluster will be marked healthy again so that vdisk creation and deletion will be operational again.

# SSD failure in slave Storage Cluster
When an SSD fails in the slave Storage Cluster the NBD server will act similarly as it acts for the Primary Storage Cluster, performing the same kind of restoring actions.
