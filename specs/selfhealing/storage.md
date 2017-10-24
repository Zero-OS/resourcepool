# NBD server
The NBD server is connected to AYS via the logging streaming offered by zero-os. If errors occur like eg an ARDB server that is not healty anymore, the NBD server will emit error logs that will be intercepted by the node.zero-os watchdog and propagated to the particular NBD service in AYS.

# NBD server failure
When an NBD server would crash, AYS will discover that instantaneously through its long living watchdog action.
AYS then needs to restarts the NBD server and the corresponding VM.

# Tlog server failure
As we deploy multiple Tlog servers per NBD server (https://github.com/zero-os/0-Disk/issues/279), AYS just needs to restart the Tlog server when it crashed.

# SSD failure in Primary Storage Cluster
When an NBD server is unable to read or write from storage engine (ARDB server) with index X, it will fail over to the slave storage cluster to continue serving blocks for shard X. At the same time it will report the failure on its stderr stream (```2::{"subject":"ardb","status":421,"data":{"address":"1.2.3.4:16379","db":41,"type":"primary","vdiskID":"vd2"}}```, see https://github.com/zero-os/0-Disk/blob/master/docs/log.md#ardb-storage-server-issues for more info) that is monitored by the long-living watchdog action of the node.zero-os service and propagated to the NBD service.

AYS will then analyze if the ARDB problem is a temporary problem, due to a reboot or restart of the ARDB server, or a permanent problem due to a disk crash to which the ARDB server is writing its blocks.

## Recovering from an outage of a storage engine (ARDB)

### Step 1: flag storage cluster to status repairing
This will prevent any creation or deletion of new vdisks.

### Step 2: notify all NBD servers that a specific storage engine is not functional
Update all impacted vdisks that a certain shard is repairing.

By means of updating the AYS model (storage_engine service) and the corresponding configuration in the etcd cluster, all NDB servers that are runnning will be notified that the storage engine is faulty (```status: offline```), and that it needs to fail over to the slave cluster for the specific shard that is offline. The vdisks which reported this issue (if it existed) will already have marked the relevant shards as `offline` (in their internal in-memory model of that cluster), and thus have no longer anything to do, when receiving this update.

Updating the AYS model needs to be done atomically, to prevent double actions, because the same problem will potentially be notified by multiple vdisks. See https://github.com/Jumpscale/ays9/issues/38

### Step 3: analyze the problem
The storage_engine service will now analyze wether the outage of the ARDB service is temporary or final. 

### Step 4: repair the problem

#### Temporary interruption of the storage_engine
If its temporary, as soon as AYS is able get the storage_engine running again (eg, wait until the node has completed rebooting, or restarted the ARDB server after a crash) it will update the AYS model and corresponding etcd configuration and assign a status (```status: repair```). This will make the running NDB servers start repairing for the relevant vdisks.

Vdisks that aren't mounted, will have to be repaired using the zeroctl tool suite. For each vdisk that has to be repaired, the `zeroctl copy dataserver` command will have to be called (e.g. ```zeroctl copy dataserver src_ip dst_ip vdiskid```).

Vdisks that were mounted and are being repaired automatically in the runtime of the relevant nbdserver, they will send a message (```2::{"subject":"ardb","status":210,"data":{"address":"1.2.3.4:16379","db":41,"type":"primary","vdiskID":"vd2"}}```, status `210` is undocumented for now, but will be used to indicate repair-complete of a vdisk's shard) to the std-err stream when the repair is complete. Note that this message is send per vdisk, not per nbdserver or shard.

A vdisk shouldn't be allowed to mount until it has been repaired (in case it had to be repaired unmounted using the zeroctl tool due to not being mounted yet).

Once all vdisks using that storage_engine have been repaired, the storage_engine service will be marked as online again (```status: online```) both in the AYS model and in the etcd cluster. On top of that the storage cluster will be marked healthy again so that vdisk creation and deletion will be operational again.

#### Permanent interruption of the storage engine
If its permanent, the storage_engine won't be able to run again, and will be given the status (```respread```). This indicates to all mounted vdisks using this dead shard, that the data on it will have to be copied from the relevant slave shard, and respread over the storage_engines which are still up and running.

vdisks (NBD servers) that are not running will be repaired using the zeroctl tool suite. For each vdisk that has to be repaired, the `zeroctl import dataserver` command will have to be called (e.g. ```zeroctl import dataserver src_ip vdiskid```).

Vdisks that were mounted and are being repaired automatically in the runtime of the relevant nbdserver, they will send a message (```2::{"subject":"ardb","status":211,"data":{"address":"1.2.3.4:16379","db":41,"type":"primary","vdiskID":"vd2"}}```, status `211` is undocumented for now, but will be used to indicate repair-and-respread-complete of a vdisk's shard) to the std-err stream when the repair is complete. Note that this message is send per vdisk, not per nbdserver or shard.

A vdisk shouldn't be allowed to mount until it has been repaired (in case it had to be repaired unmounted using the zeroctl tool due to not being mounted yet).

Once all vdisks using that storage_engine have been repaired, the storage_engine service will be marked as permanently offline (```status: rip```) both in the AYS model and in the etcd cluster. On top of that the storage cluster will be marked healthy again so that vdisk creation and deletion will be operational again.

# SSD failure in slave Storage Cluster
When an SSD fails in the slave Storage Cluster the NBD server will act similarly as it acts for the Primary Storage Cluster, performing the same kind of restoring actions.
