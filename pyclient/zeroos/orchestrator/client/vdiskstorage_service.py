class VdiskstorageService:
    def __init__(self, client):
        self.client = client



    def GetVdiskStorageInfo(self, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Get vdisk storage information
        It is method for GET /vdiskstorage/{vdiskstorageid}
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListVdiskStorages(self, headers=None, query_params=None, content_type="application/json"):
        """
        List vdisks storages
        It is method for GET /vdiskstorage
        """
        uri = self.client.base_url + "/vdiskstorage"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateNewVdiskStorage(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new vdisk storage, can be a copy from an existing vdisk
        It is method for POST /vdiskstorage
        """
        uri = self.client.base_url + "/vdiskstorage"
        return self.client.post(uri, data, headers, query_params, content_type)
