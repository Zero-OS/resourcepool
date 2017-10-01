from js9 import j

def input(job):
    service = job.service
    args = job.model.args
    block_cluster_service = service.aysrepo.serviceGet(instance=args.get('blockCluster'), role='storage_cluster')
    if 'block' != block_cluster_service.model.data.clusterType:
        raise RuntimeError('storage_cluster %s provided should be of type  block' % block_cluster_service.name)
    if args.get('objectCluster'):
        object_cluster_service = service.aysrepo.serviceGet(instance=args.get('objectCluster'), role='storage_cluster')
        if 'object' != object_cluster_service.model.data.clusterType:
            raise RuntimeError('storage_cluster %s provided should be of type  object' % object_cluster_service.name)
        if block_cluster_service.model.data.nrServer < object_cluster_service.model.data.nrServer:
                raise RuntimeError("blockStoragecluster's number of servers should be equal or larger than them in objectStoragecluster")
        if args.get('slaveCluster'):
            slave_cluster_service = service.aysrepo.serviceGet(instance=args.get('slaveCluster'), role='storage_cluster')
            if 'block' != slave_cluster_service.model.data.clusterType:
                raise RuntimeError('storage_cluster %s provided should be of type  block' % slave_cluster_service.name)
    elif args.get('slaveCluster'):
        raise RuntimeError("backup storage clusters cannot exist without an object cluster , please provide a storage cluster of type object.")
