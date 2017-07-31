from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase
import random


class VmsAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client


    @catch_exception_decoration
    def get_nodes_vms(self, nodeid):
        return self.orchestrator_client.nodes.ListVMs(nodeid=nodeid)

    @catch_exception_decoration
    def get_nodes_vms_vmid(self, nodeid, vmid):
        return self.orchestrator_client.nodes.GetVM(nodeid=nodeid, vmid=vmid)

    @catch_exception_decoration
    def get_nodes_vms_vmid_info(self, nodeid, vmid):
        return self.orchestrator_client.nodes.GetVMInfo(nodeid=nodeid, vmid=vmid)

    @catch_exception_decoration_return
    def post_nodes_vms(self, node_id, **kwargs):
        data = {"id": self.random_string(),
                "memory": random.randint(1, 16) * 1024,
                "cpu": random.randint(1, 16),
                "nics": [],
                "disks": [{
                    "vdiskid": "ubuntu-test-vdisk",
                    "maxIOps": 2000
                }],
                "userCloudInit": {},
                "systemCloudInit": {}}
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.CreateVM(nodeid=node_id, data=data)
        return response, data

    @catch_exception_decoration
    def put_nodes_vms_vmid(self, nodeid, vmid, data):
        return self.orchestrator_client.nodes.UpdateVM(nodeid=nodeid, vmid=vmid, data=data)

    @catch_exception_decoration
    def delete_nodes_vms_vmid(self, nodeid, vmid):
        return self.orchestrator_client.nodes.DeleteVM(nodeid=nodeid, vmid=vmid)

    @catch_exception_decoration
    def post_nodes_vms_vmid_start(self, nodeid, vmid):
        return self.orchestrator_client.nodes.StartVM(nodeid=nodeid, vmid=vmid, data={})

    @catch_exception_decoration
    def post_nodes_vms_vmid_stop(self, nodeid, vmid):
        return self.orchestrator_client.nodes.StopVM(nodeid=nodeid, vmid=vmid, data={})

    @catch_exception_decoration
    def post_nodes_vms_vmid_pause(self, nodeid, vmid):
        return self.orchestrator_client.nodes.PauseVM(nodeid=nodeid, vmid=vmid, data={})

    @catch_exception_decoration
    def post_nodes_vms_vmid_resume(self, nodeid, vmid):
        return self.orchestrator_client.nodes.ResumeVM(nodeid=nodeid, vmid=vmid, data={})

    @catch_exception_decoration
    def post_nodes_vms_vmid_shutdown(self, nodeid, vmid):
        return self.orchestrator_client.nodes.ShutdownVM(nodeid=nodeid, vmid=vmid, data={})

    @catch_exception_decoration
    def post_nodes_vms_vmid_migrate(self, nodeid, vmid, data):
        return self.orchestrator_client.nodes.MigrateVM(nodeid=nodeid, vmid=vmid, data=data)
