from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase


class GatewayAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def list_nodes_gateways(self, nodeid):
        return self.orchestrator_client.nodes.ListGateways(nodeid=nodeid)

    @catch_exception_decoration
    def get_nodes_gateway(self, nodeid, gwname):
        return self.orchestrator_client.nodes.GetGateway(nodeid=nodeid, gwname=gwname)

    @catch_exception_decoration_return
    def post_nodes_gateway(self, node_id, **kwargs):
        data = {
            "name": self.random_string(),
            "domain": self.random_string(),
            "nics": [],
            "portforwards": [],
            "httpproxies": []

        }
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.CreateGW(nodeid=node_id, data=data)
        return response, data

    @catch_exception_decoration
    def update_nodes_gateway(self, nodeid, gwname, data):
        return self.orchestrator_client.nodes.UpdateGateway(nodeid=nodeid, gwname=gwname, data=data)

    @catch_exception_decoration
    def delete_nodes_gateway(self, nodeid, gwname):
        response = self.orchestrator_client.nodes.DeleteGateway(nodeid=nodeid, gwname=gwname)
        return response

    @catch_exception_decoration
    def list_nodes_gateway_forwards(self, nodeid, gwname):
        return self.orchestrator_client.nodes.GetGWForwards(nodeid=nodeid, gwname=gwname)

    @catch_exception_decoration
    def post_nodes_gateway_forwards(self, nodeid, gwname, data):
        return self.orchestrator_client.nodes.CreateGWForwards(nodeid=nodeid, gwname=gwname, data=data)

    @catch_exception_decoration
    def delete_nodes_gateway_forward(self, nodeid, gwname, forwardid):
        return self.orchestrator_client.nodes.DeleteGWForward(nodeid=nodeid, gwname=gwname, forwardid=forwardid)

    @catch_exception_decoration
    def list_nodes_gateway_dhcp_hosts(self, nodeid, gwname, interface):
        return self.orchestrator_client.nodes.ListGWDHCPHosts(nodeid=nodeid, gwname=gwname, interface=interface)

    @catch_exception_decoration
    def post_nodes_gateway_dhcp_host(self, nodeid, gwname, interface, data):
        return self.orchestrator_client.nodes.AddGWDHCPHost(nodeid=nodeid, gwname=gwname, interface=interface,
                                                            data=data)

    @catch_exception_decoration
    def delete_nodes_gateway_dhcp_host(self, nodeid, gwname, interface, macaddress):
        return self.orchestrator_client.nodes.DeleteDHCPHost(nodeid=nodeid, gwname=gwname, interface=interface,
                                                             macaddress=macaddress)

    @catch_exception_decoration
    def get_nodes_gateway_advanced_http(self, nodeid, gwname):
        return self.orchestrator_client.nodes.GetGWHTTPConfig(nodeid=nodeid, gwname=gwname)

    @catch_exception_decoration
    def post_nodes_gateway_advanced_http(self, nodeid, gwname, data):
        return self.orchestrator_client.nodes.SetGWHTTPConfig(nodeid=nodeid, gwname=gwname, data=data)

    @catch_exception_decoration
    def get_nodes_gateway_advanced_firewall(self, nodeid, gwname):
        return self.orchestrator_client.nodes.GetGWFWConfig(nodeid=nodeid, gwname=gwname)

    @catch_exception_decoration
    def post_nodes_gateway_advanced_firewall(self, nodeid, gwname, data):
        return self.orchestrator_client.nodes.SetGWFWConfig(nodeid=nodeid, gwname=gwname, data=data)

    @catch_exception_decoration
    def post_nodes_gateway_start(self, nodeid, gwname):
        return self.orchestrator_client.nodes.StartGateway(nodeid=nodeid, gwname=gwname, data={})

    @catch_exception_decoration
    def post_nodes_gateway_stop(self, nodeid, gwname):
        return self.orchestrator_client.nodes.StopGateway(nodeid=nodeid, gwname=gwname, data={})

    @catch_exception_decoration
    def list_nodes_gateway_httpproxies(self, nodeid, gwname):
        return self.orchestrator_client.nodes.ListHTTPProxies(nodeid=nodeid, gwname=gwname)

    @catch_exception_decoration
    def get_nodes_gateway_httpproxy(self, nodeid, gwname, proxyid):
        return self.orchestrator_client.nodes.GetHTTPProxy(nodeid=nodeid, gwname=gwname, proxyid=proxyid)

    @catch_exception_decoration
    def get_nodes_gateway_httpproxy(self, nodeid, gwname, proxyid):
        return self.orchestrator_client.nodes.GetHTTPProxy(nodeid=nodeid, gwname=gwname, proxyid=proxyid)

    @catch_exception_decoration
    def post_nodes_gateway_httpproxy(self, nodeid, gwname, data):
        return self.orchestrator_client.nodes.CreateHTTPProxies(nodeid=nodeid, gwname=gwname, data=data)

    @catch_exception_decoration
    def delete_nodes_gateway_httpproxy(self, nodeid, gwname, proxyid):
        return self.orchestrator_client.nodes.DeleteHTTPProxies(nodeid=nodeid, gwname=gwname, proxyid=proxyid)
