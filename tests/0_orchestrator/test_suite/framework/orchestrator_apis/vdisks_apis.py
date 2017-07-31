from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase
import random


class VDisksAPIs(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_vdisks(self):
        return self.orchestrator_client.vdisks.ListVdisks()

    @catch_exception_decoration_return
    def post_vdisks(self, storagecluster, **kwargs):
        size = random.randint(1, 50)
        block_size = random.randint(1, size) * 512
        data = {"id": self.random_string(),
                "size": size,
                "blocksize": block_size,
                "type": random.choice(['boot', 'db', 'cache', 'tmp']),
                "storagecluster": storagecluster,
                "readOnly": random.choice([False, True])}
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.vdisks.CreateNewVdisk(data=data)
        return response, data

    @catch_exception_decoration
    def get_vdisks_vdiskid(self, vdiskid):
        return self.orchestrator_client.vdisks.GetVdiskInfo(vdiskid=vdiskid)

    @catch_exception_decoration
    def delete_vdisks_vdiskid(self, vdiskid):
        return self.orchestrator_client.vdisks.DeleteVdisk(vdiskid=vdiskid)

    @catch_exception_decoration
    def post_vdisks_vdiskid_resize(self, vdiskid, data):
        return self.orchestrator_client.vdisks.ResizeVdisk(vdiskid=vdiskid, data=data)

    @catch_exception_decoration
    def post_vdisks_vdiskid_rollback(self, vdiskid, data):
        return self.orchestrator_client.vdisks.RollbackVdisk(vdiskid=vdiskid, data=data)
