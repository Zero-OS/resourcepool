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
        if args.get('slaveCluster'):
            slave_cluster_service = service.aysrepo.serviceGet(instance=args.get('slaveCluster'), role='storage_cluster')
            if 'block' != slave_cluster_service.model.data.clusterType:
                raise RuntimeError('storage_cluster %s provided should be of type  block' % slave_cluster_service.name)
            if block_cluster_service.model.data.nrServer < slave_cluster_service.model.data.nrServer:
                    raise RuntimeError("blockStoragecluster's number of servers should be equal or larger than them in objectStoragecluster")
    elif args.get('slaveCluster'):
        raise RuntimeError("backup storage clusters cannot exist without an object cluster , please provide a storage cluster of type object.")


def recover_full_once(job, cluster, engine, vdisk):
    import time
    import asyncio
    loop = j.atyourservice.server.loop
    # the recovery action is granteed to run one time even if called many times (at the same time)
    # it can only be executed again when it finishes executing, otherwise callers will just return (not blocked)
    # this is to avoid executing the same recover scenario when the same error is reported via multiple nbdservers.

    from zeroos.orchestrator.sal.StorageEngine import StorageEngine
    from zeroos.orchestrator.configuration import get_jwt_token

    token = get_jwt_token(job.service.aysrepo)
    engine_sal = StorageEngine.from_ays(engine, token)

    broken = True
    for _ in range(3):
        if engine.model.data.status == 'broken':
            break
        try:
            running, _ = engine_sal.is_running()
            if running and engine_sal.is_healthy():
                broken = False
                break
        except Exception as e:
            job.logger.error("got error while checking on storage engine status: %s" % e)
            pass
        # we give it a chance to update the status
        time.sleep(2)
        engine.reload()

    if not broken:
        #Note: the restart of the machine is due too nbdserver crash on losing a connection
        #once nbdserver is fixed, there will be no need to restart the machine, and we can
        #just return in case the storage engine is not broken.
        vms = vdisk.consumers.get('vm', [])
        if len(vms) == 0:
            return
        vm = vms[0]
        j.tools.async.wrappers.sync(vm.executeAction('stop', args={"cleanup": False}, context=job.context))
        return asyncio.ensure_future(
            vm.executeAction('start', context=job.context),
            loop=loop
        )

    # TODO: sync code goes here.
    # TODO: since this method will return before the recovery of all disks
    # TODO: is not complete, there is no way to ensure the synchronization of
    # TODO: it. Unless the last bit (to wait on the rollback actions is complete.

    # force broken state and update cluster config
    engine.model.data.status = 'broken'
    engine.saveAll()

    # rewrite cluster config to etcd
    j.tools.async.wrappers.sync(cluster.executeAction('save_config', context=job.context))

    # now time to stop all the machines that relies on this
    halted = []
    rollbacks = []
    for vdisk in job.service.children:
        for vm in vdisk.consumers.get('vm', []):
            if vm.model.data.status != 'halted':
                # sync or not sync, that is the question!
                j.tools.async.wrappers.sync(vm.executeAction('stop', args={"cleanup": False}, context=job.context))
                halted.append(vm)
            action = asyncio.ensure_future(
                vdisk.executeAction('rollback', args={"timestamp": int(time.time())}, context=job.context),
                loop=loop
            )
            rollbacks.append(action)

    #TODO: We need to start the halted machine. Using the loop.run_until_coplete or the j.tools.async.wrapper.sync
    #TODO: gives an error (different ones)
    #
    # loop.run_until_complete(asyncio.gather(*rollbacks, loop=loop, return_exceptions=True))
    # job.logger.info("all rollback processes has been completed")
    #
    # for vm in halted:
    #     asyncio.ensure_future(
    #         vm.executeAction('start', context=job.context),
    #         loop=loop,
    #     )


def recover(job):
    """
    Called from nbdservers in case of ardb server failures

    message formatted as

    {
        "status": 422,
        "subject": "ardb",
        "data": {
            "address": "172.17.0.255:2000",
            "db": 0,
            "type": "primary",
            "vdiskID": "vd6"
        }
    }

    according to https://github.com/zero-os/0-Disk/blob/master/docs/log.md#ardb-storage-server-issues
    """
    service = job.service
    message = job.model.args['message']

    # so we received a recover call from one of the nbd servers due to an ardb server.
    # let's find which one has failed ...
    cluster = service.aysrepo.servicesFind(role='storage_cluster', name=service.model.data.blockCluster, first=True)
    engine = None
    for storage_engine in cluster.producers.get('storage_engine', []):
        if storage_engine.model.data.bind == message['data']['address']:
            engine = storage_engine
            break

    if engine is None:
        # we can not find the faulty engine under this vdisk storage setup.
        # message should not be directed to this vdisk storage.
        # NOTE: this can be part of the slave cluster (NotImplemented)
        job.logger.error('can not find storage engine "%s" under vdisk storage""' % (message, service.name))
        return

    vdisk_id = message['data']['vdiskID']
    vdisk = job.service.aysrepo.servicesFind(name=vdisk_id, role='vdisk', first=True)
    # now we found the faulty engine, let's see if this engine is recoverable. if so, we can simply ditch the process now
    # and hope that nbd server will pick it up again and resume normal operation. Otherwise we need to start a full recovery
    # NOTE: currently we only support full recovery
    recover_full_once(job, cluster, engine, vdisk)
