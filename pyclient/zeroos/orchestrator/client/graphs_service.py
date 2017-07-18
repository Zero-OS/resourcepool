class GraphsService:
    def __init__(self, client):
        self.client = client



    def DeleteDashboard(self, dashboardid, graphid, headers=None, query_params=None, content_type="application/json"):
        """
        Delete a dashboard
        It is method for DELETE /graphs/{graphid}/dashboards/{dashboardid}
        """
        uri = self.client.base_url + "/graphs/"+graphid+"/dashboards/"+dashboardid
        return self.client.delete(uri, None, headers, query_params, content_type)


    def GetDashboard(self, dashboardid, graphid, headers=None, query_params=None, content_type="application/json"):
        """
        Get dashboard
        It is method for GET /graphs/{graphid}/dashboards/{dashboardid}
        """
        uri = self.client.base_url + "/graphs/"+graphid+"/dashboards/"+dashboardid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListDashboards(self, graphid, headers=None, query_params=None, content_type="application/json"):
        """
        List dashboards
        It is method for GET /graphs/{graphid}/dashboards
        """
        uri = self.client.base_url + "/graphs/"+graphid+"/dashboards"
        return self.client.get(uri, None, headers, query_params, content_type)


    def CreateDashboard(self, data, graphid, headers=None, query_params=None, content_type="application/json"):
        """
        Create Dashboard
        It is method for POST /graphs/{graphid}/dashboards
        """
        uri = self.client.base_url + "/graphs/"+graphid+"/dashboards"
        return self.client.post(uri, data, headers, query_params, content_type)


    def GetGraph(self, graphid, headers=None, query_params=None, content_type="application/json"):
        """
        Get a graph
        It is method for GET /graphs/{graphid}
        """
        uri = self.client.base_url + "/graphs/"+graphid
        return self.client.get(uri, None, headers, query_params, content_type)


    def ListGraphs(self, headers=None, query_params=None, content_type="application/json"):
        """
        List all graphs
        It is method for GET /graphs
        """
        uri = self.client.base_url + "/graphs"
        return self.client.get(uri, None, headers, query_params, content_type)
