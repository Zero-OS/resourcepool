from api_testing.grid_apis.grid_pyclient_base import GridPyclientBase
from requests import HTTPError

class VmsAPI(GridPyclientBase):
    def __init__(self):
        super().__init__()

    def get_nodes_vms(self, nodeid):
        try:
            response = self.api_client.nodes.ListVMs(nodeid=nodeid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_vms_vmid(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.GetVM(nodeid=nodeid, vmid=vmid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def get_nodes_vms_vmid_info(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.GetVMInfo(nodeid=nodeid, vmid=vmid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_vms(self, nodeid, data):
        try:
            response = self.api_client.nodes.CreateVM(nodeid=nodeid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def put_nodes_vms_vmid(self, nodeid, vmid, data):
        try:
            response = self.api_client.nodes.UpdateVM(nodeid=nodeid, vmid=vmid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response
         
    def delete_nodes_vms_vmid(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.DeleteVM(nodeid=nodeid, vmid=vmid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_vms_vmid_start(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.StartVM(nodeid=nodeid, vmid=vmid, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_vms_vmid_stop(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.StopVM(nodeid=nodeid, vmid=vmid, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_vms_vmid_pause(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.PauseVM(nodeid=nodeid, vmid=vmid, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_vms_vmid_resume(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.ResumeVM(nodeid=nodeid, vmid=vmid, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response
 
    def post_nodes_vms_vmid_shutdown(self, nodeid, vmid):
        try:
            response = self.api_client.nodes.ShutdownVM(nodeid=nodeid, vmid=vmid, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_vms_vmid_migrate(self, nodeid, vmid, data):
        try:
            response = self.api_client.nodes.MigrateVM(nodeid=nodeid, vmid=vmid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response
  
