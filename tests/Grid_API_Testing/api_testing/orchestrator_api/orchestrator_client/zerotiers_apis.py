from api_testing.orchestrator_api.orchestrator_base import GridPyclientBase
from requests import HTTPError

class ZerotiersAPI(GridPyclientBase):
    def __init__(self):
        super().__init__()

    def get_nodes_zerotiers(self, nodeid):
        try:
            response = self.api_client.nodes.ListZerotier(nodeid=nodeid)
        except HTTPError as e:
            response = e.response
        return response

    def get_nodes_zerotiers_zerotierid(self, nodeid, zerotierid):
        try:
            response = self.api_client.nodes.GetZerotier(nodeid=nodeid, zerotierid=zerotierid)
        except HTTPError as e:
            response = e.response
        return response

    def post_nodes_zerotiers(self, nodeid, data):
        try:
            response = self.api_client.nodes.JoinZerotier(nodeid=nodeid, data=data)
        except HTTPError as e:
            response = e.response
        return response 

    def delete_nodes_zerotiers_zerotierid(self, nodeid, zerotierid):
        try:
            response = self.api_client.nodes.ExitZerotier(nodeid=nodeid, zerotierid=zerotierid)
        except HTTPError as e:
            response = e.response
        return response 
        
