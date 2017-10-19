from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase
import random


class VDisksAPIs(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_vdiskstorage(self):
        return self.orchestrator_client.vdiskstorage.ListVdiskStorages()

    @catch_exception_decoration_return
    def post_vdiskstorage(self, storagecluster, **kwargs):
        data = {
                "id": self.random_string(),
                "blockCluster": storagecluster
                }
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.vdiskstorage.CreateNewVdiskStorage(data=data)
        return response, data

    @catch_exception_decoration
    def get_vdiskstorage_info(self, vdiskstorageid):
        return self.orchestrator_client.vdiskstorage.GetVdiskStorageInfo(vdiskstorageid=vdiskstorageid)

    @catch_exception_decoration
    def get_import_images(self, vdiskstorageid):
        return self.orchestrator_client.vdiskstorage.ListImages(vdiskstorageid=vdiskstorageid)

    @catch_exception_decoration_return
    def post_import_image(self, vdiskstorageid, **kwargs):
        size = random.randint(15, 100)
        block_size = 2 ** random.randint(9, 15)
        export_block_size = 1048576 # should be 1048576 for image: template:ubuntu-1604
        imagename = self.random_string()
        data = {"imageName": imagename,
                "exportName": "template:ubuntu-1604",
                "exportSnapshot": "default",
                "exportBlockSize": export_block_size,
                "size": size,
                "diskBlockSize": block_size,
                "url": "ftp://hub.gig.tech"
                }

        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.vdiskstorage.ImportImage(vdiskstorageid=vdiskstorageid,data=data)
        return response, data

    @catch_exception_decoration
    def get_image_info(self, vdiskstorageid, imageid):
        return self.orchestrator_client.vdiskstorage.GetImage(vdiskstorageid=vdiskstorageid,imageid=imageid)

    @catch_exception_decoration
    def delete_image(self, vdiskstorageid, imageid):
        return self.orchestrator_client.vdiskstorage.DeleteImage(vdiskstorageid=vdiskstorageid, imageid=imageid)

    @catch_exception_decoration
    def get_vdisks(self, vdiskstorageid):
        return self.orchestrator_client.vdiskstorage.ListVdisks(vdiskstorageid=vdiskstorageid)

    @catch_exception_decoration_return
    def post_vdisks(self, vdiskstorageid, imageid="",  **kwargs):
        size = random.randint(15, 100)
        block_size = 2 ** random.randint(9, 15)
        data = {"id": self.random_string(),
                "size": size,
                "blocksize": block_size,
                "type": random.choice(['boot', 'db', 'cache', 'tmp']),
                "readOnly": random.choice([False, True])}
        data = self.update_default_data(default_data=data, new_data=kwargs)

        if data['type'] == 'boot':
            data['imageId'] = imageid
        response = self.orchestrator_client.vdiskstorage.CreateNewVdisk(vdiskstorageid=vdiskstorageid,data=data)
        return response, data

    @catch_exception_decoration
    def get_vdisks_vdiskid(self, vdiskstorageid, vdiskid):
        return self.orchestrator_client.vdiskstorage.GetVdiskInfo(vdiskstorageid=vdiskstorageid,vdiskid=vdiskid)

    @catch_exception_decoration
    def delete_vdisks_vdiskid(self, vdiskstorageid,vdiskid):
        return self.orchestrator_client.vdiskstorage.DeleteVdisk(vdiskstorageid=vdiskstorageid, vdiskid=vdiskid)

    @catch_exception_decoration
    def post_vdisks_vdiskid_resize(self, vdiskstorageid, vdiskid, data):
        return self.orchestrator_client.vdiskstorage.ResizeVdisk(vdiskstorageid=vdiskstorageid, vdiskid=vdiskid, data=data)

    @catch_exception_decoration
    def post_vdisks_vdiskid_rollback(self, vdiskstorageid, vdiskid, data):
        return self.orchestrator_client.vdiskstorage.RollbackVdisk(vdiskstorageid=vdiskstorageid, data=data)
