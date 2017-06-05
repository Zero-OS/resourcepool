class VdisksService:
    def __init__(self, client):
        self.client = client



    def ResizeVdisk(self, data, vdiskid, headers=None, query_params=None, content_type="application/json"):
        """
        Resize vdisk
        It is method for POST /vdisks/{vdiskid}/resize
        """
        uri = self.client.base_url + "/vdisks/"+vdiskid+"/resize"
        return self.client.post(uri, data, headers, query_params, content_type)


    def RollbackVdisk(self, data, vdiskid, headers=None, query_params=None, content_type="application/json"):
        """
        Rollback a vdisk to a previous state
        It is method for POST /vdisks/{vdiskid}/rollback
        """
        uri = self.client.base_url + "/vdisks/"+vdiskid+"/rollback"
        return self.client.post(uri, data, headers, query_params, content_type)


    def DeleteVdisk(self, vdiskid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete Vdisk
        It is method for DELETE /vdisks/{vdiskid}
        """
        uri = self.client.base_url + "/vdisks/"+vdiskid
        return self.client.delete(uri, headers, query_params, content_type)


    def GetVdiskInfo(self, vdiskid, headers=None, query_params=None, content_type="application/json"):
        """
        Get vdisk information
        It is method for GET /vdisks/{vdiskid}
        """
        uri = self.client.base_url + "/vdisks/"+vdiskid
        return self.client.get(uri, headers, query_params, content_type)


    def ListVdisks(self, headers=None, query_params=None, content_type="application/json"):
        """
        List vdisks
        It is method for GET /vdisks
        """
        uri = self.client.base_url + "/vdisks"
        return self.client.get(uri, headers, query_params, content_type)


    def CreateNewVdisk(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new vdisk, can be a copy from an existing vdisk
        It is method for POST /vdisks
        """
        uri = self.client.base_url + "/vdisks"
        return self.client.post(uri, data, headers, query_params, content_type)
