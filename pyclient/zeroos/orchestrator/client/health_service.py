class HealthService:
    def __init__(self, client):
        self.client = client



    def ListNodeHealth(self, nodeid, headers=None, query_params=None, content_type="application/json"):
        """
        Get detailed information of a node  health
        It is method for GET /health/nodes/{nodeid}
        """
        uri = self.client.base_url + "/health/nodes/"+nodeid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListNodesHealth(self, headers=None, query_params=None, content_type="application/json"):
        """
        List all nodes health
        It is method for GET /health/nodes
        """
        uri = self.client.base_url + "/health/nodes"
        return self.client.get(uri, None, headers, query_params, content_type)
