from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase


class ZerotiersAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_nodes_zerotiers(self, nodeid):
        return self.orchestrator_client.nodes.ListZerotier(nodeid=nodeid)

    @catch_exception_decoration
    def get_nodes_zerotiers_zerotierid(self, nodeid, zerotierid):
        return self.orchestrator_client.nodes.GetZerotier(nodeid=nodeid, zerotierid=zerotierid)

    @catch_exception_decoration_return
    def post_nodes_zerotiers(self, nodeid, **kwargs):
        data = {'nwid': ''}
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.JoinZerotier(nodeid=nodeid, data=data)
        return response, data

    @catch_exception_decoration
    def delete_nodes_zerotiers_zerotierid(self, nodeid, zerotierid):
        return self.orchestrator_client.nodes.ExitZerotier(nodeid=nodeid, zerotierid=zerotierid)
