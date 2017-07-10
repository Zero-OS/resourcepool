from api_testing.grid_apis.orchestrator_base import GridPyclientBase
from requests import HTTPError

class BridgesAPI(GridPyclientBase):
    def __init__(self):
        super().__init__()

    def get_nodes_bridges(self, nodeid):
        try:
            response = self.api_client.nodes.ListBridges(nodeid=nodeid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_bridges_bridgeid(self, nodeid, bridgeid):
        try:
            response = self.api_client.nodes.GetBridge(nodeid=nodeid, bridgeid=bridgeid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_bridges(self, nodeid, data):
        try:
            response = self.api_client.nodes.CreateBridge(nodeid=nodeid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_bridges_bridgeid(self, nodeid, bridgeid):
        try:
            response = self.api_client.nodes.DeleteBridge(nodeid=nodeid, bridgeid=bridgeid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
        