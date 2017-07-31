from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase


class Storageclusters(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration_return
    def post_storageclusters(self, node_id, **kwargs):
        data = {
            "label": self.random_string(),
            "servers": 1,
            "driveType": 'ssd',
            "clusterType": "storage",
            "nodes": [node_id]
        }
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.storageclusters.DeployNewCluster(data=data)
        return response, data

    @catch_exception_decoration
    def get_storageclusters(self):
        return self.orchestrator_client.storageclusters.ListAllClusters()

    @catch_exception_decoration
    def get_storageclusters_label(self, label):
        return self.orchestrator_client.storageclusters.GetClusterInfo(label=label)

    @catch_exception_decoration
    def delete_storageclusters_label(self, label):
        return self.orchestrator_client.storageclusters.KillCluster(label=label)
