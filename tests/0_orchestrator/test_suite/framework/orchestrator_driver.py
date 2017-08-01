from framework.orchestrator_apis.bridges_apis import BridgesAPI
from framework.orchestrator_apis.containers_apis import ContainersAPI
from framework.orchestrator_apis.gateways_apis import GatewayAPI
from framework.orchestrator_apis.nodes_apis import NodesAPI
from framework.orchestrator_apis.storageclusters_apis import Storageclusters
from framework.orchestrator_apis.storagepools_apis import StoragepoolsAPI
from framework.orchestrator_apis.vms_apis import VmsAPI
from framework.orchestrator_apis.vdisks_apis import VDisksAPIs
from framework.orchestrator_apis.zerotiers_apis import ZerotiersAPI
from zeroos.orchestrator import client
from testconfig import config


class OrchasteratorDriver:
    api_base_url = config['main']['api_base_url']
    client_id = config['main']['client_id']
    client_secret = config['main']['client_secret']
    organization = config['main']['organization']
    zerotier_token = config['main']['zerotier_token']

    def __init__(self):
        self.JWT = None
        self.orchestrator_client = client.APIClient(self.api_base_url)
        self.refresh_jwt()

        self.bridges_api = BridgesAPI(self)
        self.container_api = ContainersAPI(self)
        self.gateway_api = GatewayAPI(self)
        self.nodes_api = NodesAPI(self)
        self.storagepools_api = StoragepoolsAPI(self)
        self.storageclusters_api = Storageclusters(self)
        self.vdisks_api = VDisksAPIs(self)
        self.vms_api = VmsAPI(self)
        self.zerotiers_api = ZerotiersAPI(self)

        self.nodes_info = self.get_node_info()

    def get_jwt(self):
        auth = client.oauth2_client_itsyouonline.Oauth2ClientItsyouonline()
        response = auth.get_access_token(self.client_id, self.client_secret,
                                         scopes=['user:memberof:%s' % self.organization],
                                         audiences=[])
        return response.content.decode('utf-8')

    def refresh_jwt(self):
        self.JWT = self.get_jwt()
        self.orchestrator_client.set_auth_header("Bearer %s" % self.JWT)

    def get_node_info(self):
        nodes_info = []
        response = self.nodes_api.get_nodes()
        for node in response.json():
            if node['status'] == 'halted':
                continue
            nodes_info.append({"id": node['id'],
                               "ip": node['ipaddress'],
                               "status": node['status']})
        return nodes_info
