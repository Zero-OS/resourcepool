from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase
import random


class StoragepoolsAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_storagepools(self, nodeid):
        return self.orchestrator_client.nodes.ListStoragePools(nodeid=nodeid)

    @catch_exception_decoration_return
    def post_storagepools(self, node_id, free_devices, **kwargs):
        data = {"name": self.random_string(),
                "metadataProfile": 'single',
                "dataProfile": 'single',
                "devices": [random.choice(free_devices)]}

        if len(free_devices) > 4:
            data['metadataProfile'] = random.choice(['raid0', 'raid1', 'raid5', 'raid6', 'raid10', 'dup', 'single'])
            data['dataProfile'] = random.choice(['raid0', 'raid1', 'raid5', 'raid6', 'raid10', 'dup', 'single'])
            data['devices'] = free_devices[:4]

        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.CreateStoragePool(nodeid=node_id, data=data)
        return response, data

    @catch_exception_decoration
    def get_storagepools_storagepoolname(self, nodeid, storagepoolname):
        return self.orchestrator_client.nodes.GetStoragePoolInfo(nodeid=nodeid, storagepoolname=storagepoolname)

    @catch_exception_decoration
    def delete_storagepools_storagepoolname(self, nodeid, storagepoolname):
        return self.orchestrator_client.nodes.DeleteStoragePool(nodeid=nodeid, storagepoolname=storagepoolname)

    @catch_exception_decoration
    def get_storagepools_storagepoolname_devices(self, nodeid, storagepoolname):
        return self.orchestrator_client.nodes.ListStoragePoolDevices(nodeid=nodeid, storagepoolname=storagepoolname)

    @catch_exception_decoration
    def post_storagepools_storagepoolname_devices(self, nodeid, storagepoolname, data):
        return self.orchestrator_client.nodes.CreateStoragePoolDevices(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                       data=data)

    @catch_exception_decoration
    def get_storagepools_storagepoolname_devices_deviceid(self, nodeid, storagepoolname, deviceuuid):
        return self.orchestrator_client.nodes.GetStoragePoolDeviceInfo(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                       deviceuuid=deviceuuid)

    @catch_exception_decoration
    def delete_storagepools_storagepoolname_devices_deviceid(self, nodeid, storagepoolname, deviceuuid):
        return self.orchestrator_client.nodes.DeleteStoragePoolDevice(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                      deviceuuid=deviceuuid)

    @catch_exception_decoration
    def get_storagepools_storagepoolname_filesystems(self, nodeid, storagepoolname):
        return self.orchestrator_client.nodes.ListFilesystems(nodeid=nodeid, storagepoolname=storagepoolname)

    @catch_exception_decoration
    def post_storagepools_storagepoolname_filesystems(self, node_id, storagepoolname, **kwargs):
        data = {"name": self.random_string(),
                "quota": random.randint(0, 10)}
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.CreateFilesystem(nodeid=node_id, storagepoolname=storagepoolname,
                                                                   data=data)
        return response, data

    @catch_exception_decoration
    def get_storagepools_storagepoolname_filesystems_filesystemname(self, nodeid, storagepoolname, filesystemname):
        return self.orchestrator_client.nodes.GetFilesystemInfo(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                filesystemname=filesystemname)

    @catch_exception_decoration
    def delete_storagepools_storagepoolname_filesystems_filesystemname(self, nodeid, storagepoolname, filesystemname):
        return self.orchestrator_client.nodes.DeleteFilesystem(nodeid=nodeid, storagepoolname=storagepoolname,
                                                               filesystemname=filesystemname)

    @catch_exception_decoration
    def get_filesystem_snapshots(self, nodeid, storagepoolname, filesystemname):
        return self.orchestrator_client.nodes.ListFilesystemSnapshots(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                      filesystemname=filesystemname)

    @catch_exception_decoration
    def post_filesystems_snapshots(self, nodeid, storagepoolname, filesystemname, **kwargs):
        data = {'name': self.random_string()}
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.CreateSnapshot(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                 filesystemname=filesystemname,
                                                                 data=data)
        return response, data

    @catch_exception_decoration
    def get_filesystem_snapshots_snapshotname(self, nodeid, storagepoolname, filesystemname, snapshotname):
        return self.orchestrator_client.nodes.GetFilesystemSnapshotInfo(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                        filesystemname=filesystemname,
                                                                        snapshotname=snapshotname)

    @catch_exception_decoration
    def delete_filesystem_snapshots_snapshotname(self, nodeid, storagepoolname, filesystemname, snapshotname):
        return self.orchestrator_client.nodes.DeleteFilesystemSnapshot(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                       filesystemname=filesystemname,
                                                                       snapshotname=snapshotname)

    @catch_exception_decoration
    def post_filesystem_snapshots_snapshotname_rollback(self, nodeid, storagepoolname, filesystemname, snapshotname,
                                                        data):
        return self.orchestrator_client.nodes.RollbackFilesystemSnapshot(nodeid=nodeid, storagepoolname=storagepoolname,
                                                                         filesystemname=filesystemname,
                                                                         snapshotname=snapshotname,
                                                                         data=data)
