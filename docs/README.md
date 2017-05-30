# Zero-OS 0-rest-api

A Zero-OS 0 Rest API is a cluster of Zero-OS nodes, exposing its services through a Zero-OS Rest API Server.

In the below picture you see a 0 Rest API of 5 physical nodes, all connected through a ZeroTier network.

![Architecture](resource-pool.png)

Next to the the G8OS nodes, a Zero-OS Rest API includes the following components:
- One **Zero-OS Rest API Server**, exposing all the APIs to manage and interacting with the resource pool
- One **AYS Server**, for managing the full lifecycle of both the 0 Rest API and the actual workloads (applications)
- One **iPXE Server** from which all Zero-OS nodes boot

Both the **Zero-OS Rest API Server**, the **AYS Server** and the **iPXE Server** run in a container on one of the Zero-OS Rest API nodes, or on any other local or remote host, connected to the same ZeroTier network as the other Zero-OS nodes in the resource pool.

In addition a Zero-OS Rest API typically includes one or more **Storage Clusters**, implemented as clusters of (ARDB) key-value stores running in containers hosted on the Zero-OS Rest API nodes. In the above picture two storage clusters are shown:
- One for implementing a block storage backend, exposed through NBD servers, one for each each virtual machine using virtual disks from the block storage backend
- Another one implementing the backend for the TLOG server, needed by the NBD servers

Furthermore the above setup shows a NAS server and a S3 server, both running in a container, and both connected to the second storage cluster, the same one that is used by the TLOG server.

For more details see:
* [Setting up the Resource Pool](setup/setup.md)
* [Zero-OS Rest API](api.md)
* [Storage Cluster](storagecluster/storagecluster.md)
* [Block Storage](blockstorage/blockstorage.md)

Or see the full [table of contents](SUMMARY.md) for other topics.

In [Getting Started with Zero-OS Rest API](gettingstarted/gettingstarted.md) you find a recommended path to get quickly up and running.
