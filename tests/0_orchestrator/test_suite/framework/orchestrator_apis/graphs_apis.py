import json
from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase


class GraphsAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_graphs(self):
        return self.orchestrator_client.graphs.ListGraphs()

    @catch_exception_decoration
    def get_graphs_graphid(self, graphid):
        return self.orchestrator_client.graphs.GetGraph(graphid=graphid)

    @catch_exception_decoration_return
    def put_graphs_graphid(self, graphid, **kwargs):
        data = {
            'id': self.random_string(),
            'url': ''
        }
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.graphs.UpdateGraph(graphid=graphid, data=data)
        return response, data
    
    @catch_exception_decoration
    def get_dashboards(self, graphid):
        return self.orchestrator_client.graphs.ListDashboards(graphid=graphid)

    @catch_exception_decoration
    def get_dashboard_dashboardname(self, graphid, dashboardname):
        return self.orchestrator_client.graphs.GetDashboard(graphid=graphid, dashboardname=dashboardname)

    @catch_exception_decoration
    def get_dashboard_dashboardname(self, graphid, dashboardname):
        return self.orchestrator_client.graphs.GetDashboard(graphid=graphid, dashboardname=dashboardname)

    @catch_exception_decoration_return
    def post_dashboard(self, graphid, **kwargs):
        data = {
            'name': self.random_string(),
            'dashboard': json.dumps({'id':self.random_string(), 'title':self.random_string()})
        }
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.graphs.CreateDashboard(graphid=graphid, data=data)
        return response, data

    @catch_exception_decoration
    def delete_dashboard_dashboardname(self, graphid, dashboardname):
        return self.orchestrator_client.graphs.DeleteDashboard(graphid=graphid, dashboardname=dashboardname)