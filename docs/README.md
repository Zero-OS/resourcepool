# Zero-OS Orchestrator

The Zero-OS Orchestrator is the RESTful API server for managing a cluster of Zero-OS nodes.

In the below picture you see a Zero-OS cluster with 5 physical nodes, all running Zero-OS, and all connected to a ZeroTier management network.

![Architecture](architecture.png)

Next to the the Zero-OS nodes, a Zero-OS cluster includes the following components:
- **Zero-OS Orchestrator**, exposing all the RESTful APIs to manage and interact with the Zero-OS cluster
- **AYS Server**, for managing the full lifecycle of both the Zero-OS cluster and the actual workloads (applications)
- **iPXE Server** from which all Zero-OS nodes boot

Both the **Zero-OS Orchestrator**, the **AYS Server** and the **iPXE Server** run in containers on one of the Zero-OS nodes, or on any other local or remote host, connected to the same ZeroTier management network as the other Zero-OS nodes in the cluster.

In addition, a Zero-OS cluster typically hosts (as a workload) one or more **Storage Clusters**, implemented as clusters of key-value stores running in containers hosted on the Zero-OS nodes. In the above picture three storage clusters are shown, all implemented using ARDB in combination with RocksDB:
- Two using SSD storage
- One using HDD storage

Together they implement the block storage of the Zero-OS cluster. For each virtual disk there will one container running a NBD server that uses the primary SSD storage cluster and reliabably forwards all transactions to another container running the Transaction Log (TLOG) server, which in turn uses the secondary SSD storage cluster and HDD storage cluster.

For more details see:
* [Setting up the Zero-OS cluster](setup/README.md)
* [Zero-OS Orchestrator RESTful API](api/README.md)
* [Storage Cluster](storagecluster/README.md)
* [Block Storage](blockstorage/README.md)
* [Networking](networking/README.md)

See the full [table of contents](SUMMARY.md) for all topics.

In [Getting Started with Zero-OS Orchestrator](gettingstarted/README.md) you find a recommended path to get quickly up and running.
