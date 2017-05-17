# G8OS Resource Pool

A G8OS resource pool is a cluster of G8OS nodes, exposing its services through a Resource Pool API Server.

In the below picture you see a resource pool of 5 physical nodes, all connected through a ZeroTier network.

![Architecture](resource-pool.png)

Next to the the G8OS nodes, a G8OS resource pool includes the following components:
- One **Resource Pool API Server**, exposing all the APIs to manage and interacting with the resource pool
- One **AYS Server**, for managing the full lifecycle of both the resource pool and the actual workloads (applications)
- One **iPXE Server** from which all G8OS nodes boot

Both the **Resource Pool API Server**, the **AYS Server** and the **iPXE Server** run in a container on one of the G8OS resource pool nodes, or on any other local or remote host, connected to the same ZeroTier network as the other G8OS nodes in the resource pool.

In addition a G8OS resource pool typically includes one or more **Storage Clusters**, implemented as clusters of (ARDB) key-value stores running in containers hosted on the G8OS resource pool nodes. In the above picture two storage clusters are shown:
- One for implementing a block storage backend, exposed through NBD servers, one for each each virtual machine using virtual disks from the block storage backend
- Another one implementing the backend for the TLOG server, needed by the NBD servers

Furthermore the above setup shows a NAS server and a S3 server, both running in a container, and both connected to the second storage cluster, the same one that is used by the TLOG server.

For more details see:
* [Setting up the Resource Pool](setup/setup.md)
* [Resource Pool API](api.md)
* [Storage Cluster](storagecluster/storagecluster.md)
* [Block Storage](blockstorage/blockstorage.md)

Or see the full [table of contents](SUMMARY.md) for other topics.

In [Getting Started with G8OS Resource Pool](gettingstarted/gettingstarted.md) you find a recommended path to get quickly up and running.
