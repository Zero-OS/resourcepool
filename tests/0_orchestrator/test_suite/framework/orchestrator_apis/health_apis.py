from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase


class HealthcheckAPI:
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_all_nodes_health(self):
        return self.orchestrator_client.health.ListNodesHealth()

    @catch_exception_decoration
    def get_node_health(self, node_id):
        return self.orchestrator_client.health.ListNodeHealth(nodeid=node_id)

    @catch_exception_decoration
    def get_storageclusters_health(self):
        return self.orchestrator_client.health.ListStorageClustersHealth()

    @catch_exception_decoration
    def get_storagecluster_health(self, storageclusterid):
        return self.orchestrator_client.health.ListStorageClusterHealth(storageclusterid=storageclusterid)
