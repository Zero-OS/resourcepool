class VdiskstorageService:
    def __init__(self, client):
        self.client = client



    def DeleteImage(self, imageid, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete an vdisk image from the VdiskStorage
        It is method for DELETE /vdiskstorage/{vdiskstorageid}/images/{imageid}
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/images/"+imageid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetImage(self, imageid, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detail about a vdisk image
        It is method for GET /vdiskstorage/{vdiskstorageid}/images/{imageid}
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/images/"+imageid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListImages(self, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        List all vdisk images installed in this VdiskStroage
        It is method for GET /vdiskstorage/{vdiskstorageid}/images
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/images"
        return self.client.get(uri, None, headers, query_params, content_type)


    def ImportImage(self, data, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Import an image from an FTP server into the VdiskStorage
        It is method for POST /vdiskstorage/{vdiskstorageid}/images
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/images"
        return self.client.post(uri, data, headers, query_params, content_type)


    def ResizeVdisk(self, data, vdiskid, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Resize vdisk
        It is method for POST /vdiskstorage/{vdiskstorageid}/vdisks/{vdiskid}/resize
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/vdisks/"+vdiskid+"/resize"
        return self.client.post(uri, data, headers, query_params, content_type)


    def RollbackVdisk(self, data, vdiskid, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Rollback a vdisk to a previous state
        It is method for POST /vdiskstorage/{vdiskstorageid}/vdisks/{vdiskid}/rollback
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/vdisks/"+vdiskid+"/rollback"
        return self.client.post(uri, data, headers, query_params, content_type)


    def DeleteVdisk(self, vdiskid, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete Vdisk
        It is method for DELETE /vdiskstorage/{vdiskstorageid}/vdisks/{vdiskid}
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/vdisks/"+vdiskid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetVdiskInfo(self, vdiskid, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Get vdisk information
        It is method for GET /vdiskstorage/{vdiskstorageid}/vdisks/{vdiskid}
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/vdisks/"+vdiskid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListVdisks(self, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        List vdisks
        It is method for GET /vdiskstorage/{vdiskstorageid}/vdisks
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/vdisks"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateNewVdisk(self, data, vdiskstorageid, headers=None, query_params=None, content_type="application/json"):
        """
        Create a new vdisk, can be a copy from an existing vdisk
        It is method for POST /vdiskstorage/{vdiskstorageid}/vdisks
        """
        uri = self.client.base_url + "/vdiskstorage/"+vdiskstorageid+"/vdisks"
        return self.client.post(uri, data, headers, query_params, content_type)


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
        Create a new vdisk storage
        It is method for POST /vdiskstorage
        """
        uri = self.client.base_url + "/vdiskstorage"
        return self.client.post(uri, data, headers, query_params, content_type)
