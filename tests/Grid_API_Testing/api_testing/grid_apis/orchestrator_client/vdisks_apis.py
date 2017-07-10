from api_testing.grid_apis.orchestrator_base import GridPyclientBase
from requests import HTTPError

class VDisksAPIs(GridPyclientBase):
    def __init__(self):
        super().__init__()

    def get_vdisks(self):
        try:
            response = self.api_client.vdisks.ListVdisks()
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_vdisks(self, data):
        try:
            response = self.api_client.vdisks.CreateNewVdisk(data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response
   
    def get_vdisks_vdiskid(self, vdiskid):
        try:
            response = self.api_client.vdisks.GetVdiskInfo(vdiskid=vdiskid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
        
    def delete_vdisks_vdiskid(self, vdiskid):
        try:
            response = self.api_client.vdisks.DeleteVdisk(vdiskid=vdiskid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
    
    def post_vdisks_vdiskid_resize(self, vdiskid, data):
        try:
            response = self.api_client.vdisks.ResizeVdisk(vdiskid=vdiskid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response
        
    def post_vdisks_vdiskid_rollback(self, vdiskid, data):
        try:
            response = self.api_client.vdisks.RollbackVdisk(vdiskid=vdiskid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response