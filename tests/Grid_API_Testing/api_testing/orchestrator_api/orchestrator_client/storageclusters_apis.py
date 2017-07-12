from api_testing.orchestrator_api.orchestrator_base import GridPyclientBase
from requests import HTTPError

class Storageclusters(GridPyclientBase):
    def __init__(self):
        super().__init__()

    def post_storageclusters(self, data):
        try:
            response = self.api_client.storageclusters.DeployNewCluster(data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_storageclusters(self):
        try:
            response = self.api_client.storageclusters.ListAllClusters()
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_storageclusters_label(self, label):
        try:
            response = self.api_client.storageclusters.GetClusterInfo(label=label)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_storageclusters_label(self, label):
        try:
            response = self.api_client.storageclusters.KillCluster(label=label)
        except HTTPError as e:
            response = e.response
        finally:
            return response   
