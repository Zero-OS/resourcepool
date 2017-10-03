from js9 import j

def input(job):
    service = job.service
    args = job.model.args
    block_cluster_service = service.aysrepo.serviceGet(instance=args.get('blockCluster'), role='storage_cluster')
    if args.get('objectCluster'):
        if args.get('slaveCluster'):
            slave_cluster_service = service.aysrepo.serviceGet(instance=args.get('slaveCluster'), role='storage_cluster')
            if block_cluster_service.model.data.nrServer < slave_cluster_service.model.data.nrServer:
                    raise RuntimeError("blockStoragecluster's number of servers should be equal or larger than them in objectStoragecluster")
    elif args.get('slaveCluster'):
        raise RuntimeError("backup storage clusters cannot exist without an object cluster , please provide a storage cluster of type object.")
