from js9 import j

def input(job):
    service = job.service
    args = job.model.args
    block_cluster_service = service.aysrepo.serviceGet(instance=args.get('blockCluster'), role='storage_cluster')
    if 'block' != block_cluster_service.model.data.clusterType:
        raise RuntimeError('storage_cluster %s provided should be of type  block' % block_cluster_service.name)
    object_cluster_service = service.aysrepo.serviceGet(instance=args.get('objectCluster'), role='storage_cluster')
    if 'object' != object_cluster_service.model.data.clusterType:
        raise RuntimeError('storage_cluster %s provided should be of type  object' % object_cluster_service.name)
    slave_cluster_service = service.aysrepo.serviceGet(instance=args.get('slaveCluster'), role='storage_cluster')
    if 'block' != slave_cluster_service.model.data.clusterType:
        raise RuntimeError('storage_cluster %s provided should be of type  block' % slave_cluster_service.name)
