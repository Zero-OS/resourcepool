from api_testing.orchestrator_api.orchestrator_base import GridPyclientBase
from requests import HTTPError

class StoragepoolsAPI(GridPyclientBase):
    def __init__(self):
        super().__init__()

    def get_storagepools(self, nodeid):
        try:
            response = self.api_client.nodes.ListStoragePools(nodeid=nodeid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_storagepools(self, nodeid, data):
        try:
            response = self.api_client.nodes.CreateStoragePool(nodeid=nodeid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def get_storagepools_storagepoolname(self, nodeid, storagepoolname):
        try:
            response = self.api_client.nodes.GetStoragePoolInfo(nodeid=nodeid, storagepoolname=storagepoolname)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def delete_storagepools_storagepoolname(self, nodeid, storagepoolname):
        try:
            response = self.api_client.nodes.DeleteStoragePool(nodeid=nodeid, storagepoolname=storagepoolname)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def get_storagepools_storagepoolname_devices(self, nodeid, storagepoolname):
        try:
            response = self.api_client.nodes.ListStoragePoolDevices(nodeid=nodeid, storagepoolname=storagepoolname)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def post_storagepools_storagepoolname_devices(self, nodeid, storagepoolname, data):
        try:
            response = self.api_client.nodes.CreateStoragePoolDevices(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                                     data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def get_storagepools_storagepoolname_devices_deviceid(self, nodeid, storagepoolname, deviceuuid):
        try:
            response = self.api_client.nodes.GetStoragePoolDeviceInfo(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                                     deviceuuid=deviceuuid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def delete_storagepools_storagepoolname_devices_deviceid(self, nodeid, storagepoolname, deviceuuid):
        try:
            response = self.api_client.nodes.DeleteStoragePoolDevice(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                                    deviceuuid=deviceuuid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def get_storagepools_storagepoolname_filesystems(self, nodeid, storagepoolname):
        try:
            response = self.api_client.nodes.ListFilesystems(nodeid=nodeid, storagepoolname=storagepoolname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_storagepools_storagepoolname_filesystems(self, nodeid, storagepoolname, data):
        try:
            response = self.api_client.nodes.CreateFilesystem(nodeid=nodeid, storagepoolname=storagepoolname, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_storagepools_storagepoolname_filesystems_filesystemname(self, nodeid, storagepoolname, filesystemname):  
        try:
            response = self.api_client.nodes.GetFilesystemInfo(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                          filesystemname=filesystemname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_storagepools_storagepoolname_filesystems_filesystemname(self, nodeid, storagepoolname, filesystemname):
        try:
            response = self.api_client.nodes.DeleteFilesystem(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                             filesystemname=filesystemname)
        except HTTPError as e:
            response = e.response
        finally:
            return response


    def get_filesystem_snapshots(self, nodeid, storagepoolname, filesystemname):
        try:
            response = self.api_client.nodes.ListFilesystemSnapshots(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                                    filesystemname=filesystemname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_filesystems_snapshots(self, nodeid, storagepoolname, filesystemname, data):
        try:
            response = self.api_client.nodes.CreateSnapshot(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                           filesystemname=filesystemname, 
                                                                           data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response


    def get_filesystem_snapshots_snapshotname(self, nodeid, storagepoolname, filesystemname, snapshotname):
        try:
            response = self.api_client.nodes.GetFilesystemSnapshotInfo(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                                      filesystemname=filesystemname, 
                                                                                      snapshotname=snapshotname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_filesystem_snapshots_snapshotname(self, nodeid, storagepoolname, filesystemname, snapshotname):
        try:
            response = self.api_client.nodes.DeleteFilesystemSnapshot(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                                     filesystemname=filesystemname, 
                                                                                     snapshotname=snapshotname)
        except HTTPError as e:
            response = e.response
        finally:
            return response


    def post_filesystem_snapshots_snapshotname_rollback(self, nodeid, storagepoolname, filesystemname, snapshotname, data):
        try:
            response = self.api_client.nodes.RollbackFilesystemSnapshot(nodeid=nodeid, storagepoolname=storagepoolname, 
                                                                                       filesystemname=filesystemname, 
                                                                                       snapshotname=snapshotname, 
                                                                                       data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response
