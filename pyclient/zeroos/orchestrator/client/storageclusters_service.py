class StorageclustersService:
    def __init__(self, client):
        self.client = client



    def KillCluster(self, label, headers=None, query_params=None, content_type="application/json"):
        """
        Kill cluster
        It is method for DELETE /storageclusters/{label}
        """
        uri = self.client.base_url + "/storageclusters/"+label
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetClusterInfo(self, label, headers=None, query_params=None, content_type="application/json"):
        """
        Get full information about specific cluster
        It is method for GET /storageclusters/{label}
        """
        uri = self.client.base_url + "/storageclusters/"+label
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListAllClusters(self, headers=None, query_params=None, content_type="application/json"):
        """
        List all running clusters
        It is method for GET /storageclusters
        """
        uri = self.client.base_url + "/storageclusters"
        return self.client.get(uri, None, headers, query_params, content_type)


    def DeployNewCluster(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Deploy new cluster
        It is method for POST /storageclusters
        """
        uri = self.client.base_url + "/storageclusters"
        return self.client.post(uri, data, headers, query_params, content_type)
