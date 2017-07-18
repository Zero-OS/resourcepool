from api_testing.orchestrator_api.orchestrator_base import GridPyclientBase
from requests import HTTPError

class GatewayAPI(GridPyclientBase):
    def __init__(self):
        super().__init__()
        self.createdGw = []

    def list_nodes_gateways(self, nodeid):
        try:
            response = self.api_client.nodes.ListGateways(nodeid=nodeid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_gateway(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.GetGateway(nodeid=nodeid, gwname=gwname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_gateway(self, nodeid, data):
        try:
            response = self.api_client.nodes.CreateGW(nodeid=nodeid, data=data)
            if response.status_code == 201:
                self.createdGw.append({"node": nodeid, "name": data["name"]})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def update_nodes_gateway(self, nodeid, gwname, data):
        try:
            response = self.api_client.nodes.UpdateGateway(nodeid=nodeid, gwname=gwname, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_gateway(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.DeleteGateway(nodeid=nodeid, gwname=gwname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def list_nodes_gateway_forwards(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.GetGWForwards(nodeid=nodeid, gwname=gwname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_gateway_forwards(self, nodeid, gwname, data):
        try:
            response = self.api_client.nodes.CreateGWForwards(nodeid=nodeid, gwname=gwname, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_gateway_forward(self, nodeid, gwname, forwardid):
        try:
            response = self.api_client.nodes.DeleteGWForward(nodeid=nodeid, gwname=gwname, forwardid=forwardid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def list_nodes_gateway_dhcp_hosts(self, nodeid, gwname, interface):
        try:
            response = self.api_client.nodes.ListGWDHCPHosts(nodeid=nodeid, gwname=gwname, interface=interface)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_gateway_dhcp_host(self, nodeid, gwname, interface, data):
        try:
            response = self.api_client.nodes.AddGWDHCPHost(nodeid=nodeid, gwname=gwname, interface=interface, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_gateway_dhcp_host(self, nodeid, gwname, interface, macaddress):
        try:
            response = self.api_client.nodes.DeleteDHCPHost(nodeid=nodeid, gwname=gwname, interface=interface, macaddress=macaddress)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_gateway_advanced_http(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.GetGWHTTPConfig(nodeid=nodeid, gwname=gwname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_gateway_advanced_http(self, nodeid, gwname, data):
        try:
            response = self.api_client.nodes.SetGWHTTPConfig(nodeid=nodeid, gwname=gwname, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_gateway_advanced_firewall(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.GetGWFWConfig(nodeid=nodeid, gwname=gwname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_gateway_advanced_firewall(self, nodeid, gwname, data):
        try:
            response = self.api_client.nodes.SetGWFWConfig(nodeid=nodeid, gwname=gwname, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response


    def post_nodes_gateway_start(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.StartGateway(nodeid=nodeid, gwname=gwname, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_gateway_stop(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.StopGateway(nodeid=nodeid, gwname=gwname, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def list_nodes_gateway_httpproxies(self, nodeid, gwname):
        try:
            response = self.api_client.nodes.ListHTTPProxies(nodeid=nodeid, gwname=gwname)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_gateway_httpproxy(self, nodeid, gwname, proxyid):
        try:
            response = self.api_client.nodes.GetHTTPProxy(nodeid=nodeid, gwname=gwname, proxyid=proxyid)
        except HTTPError as e:
            response = e.response
        finally:
            return response


    def get_nodes_gateway_httpproxy(self, nodeid, gwname, proxyid):
        try:
            response = self.api_client.nodes.GetHTTPProxy(nodeid=nodeid, gwname=gwname, proxyid=proxyid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_gateway_httpproxy(self, nodeid, gwname, data):
        try:
            response = self.api_client.nodes.CreateHTTPProxies(nodeid=nodeid, gwname=gwname, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_gateway_httpproxy(self, nodeid, gwname, proxyid):
        try:
            response = self.api_client.nodes.DeleteHTTPProxies(nodeid=nodeid, gwname=gwname, proxyid=proxyid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
