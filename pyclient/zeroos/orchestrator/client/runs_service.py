class RunsService:
    def __init__(self, client):
        self.client = client



    def WaitOnRun(self, runid, headers=None, query_params=None, content_type="application/json"):
        """
        Wait for Run
        It is method for GET /runs/{runid}/wait
        """
        uri = self.client.base_url + "/runs/"+runid+"/wait"
        return self.client.get(uri, None, headers, query_params, content_type)


    def GetRunState(self, runid, headers=None, query_params=None, content_type="application/json"):
        """
        Get Run Status
        It is method for GET /runs/{runid}
        """
        uri = self.client.base_url + "/runs/"+runid
        return self.client.get(uri, None, headers, query_params, content_type)
