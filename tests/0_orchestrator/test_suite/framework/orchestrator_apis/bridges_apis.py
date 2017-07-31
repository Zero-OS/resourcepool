from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase
import random


class BridgesAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client
        self.createdbridges = []

    @catch_exception_decoration
    def get_nodes_bridges(self, nodeid):
        return self.orchestrator_client.nodes.ListBridges(nodeid=nodeid)

    @catch_exception_decoration
    def get_nodes_bridges_bridgeid(self, nodeid, bridgeid):
        return self.orchestrator_client.nodes.GetBridge(nodeid=nodeid, bridgeid=bridgeid)

    @catch_exception_decoration_return
    def post_nodes_bridges(self, node_id, **kwargs):
        temp = random.randint(1, 254)
        if 'networkMode' not in kwargs.keys():
            kwargs['networkMode'] = self.random_choise(["none", "static", "dnsmasq"])

        settings_draft = {"none": {},
                          "static": {"cidr": "192.168.%i.%i/16" % (random.randint(1, 254), random.randint(1, 254))},
                          "dnsmasq": {"cidr": "192.168.%i.1/16" % temp, "start": "192.168.%i.2" % temp,
                                      "end": "192.168.%i.254" % temp}}

        data = {"name": self.random_string(),
                "hwaddr": self.randomMAC(),
                "networkMode": kwargs['networkMode'],
                "nat": self.random_choise(([False, True])),
                "setting": settings_draft[kwargs['networkMode']]
                }
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.CreateBridge(nodeid=node_id,
                                                               data=data)
        if response.status_code == 201:
            self.createdbridges.append({"node": node_id, "name": data["name"]})
        return response, data

    @catch_exception_decoration
    def delete_nodes_bridges_bridgeid(self, nodeid, bridgeid):
        response = self.orchestrator_client.nodes.DeleteBridge(nodeid=nodeid, bridgeid=bridgeid)
        if response.status_code == 204:
            self.createdbridges.remove({"node": nodeid, "name": bridgeid})
        return response
