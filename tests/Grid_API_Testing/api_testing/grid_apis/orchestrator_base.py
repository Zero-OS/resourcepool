from zeroos.orchestrator import client as apiclient
from api_testing.grid_apis import api_base_url, JWT 
from testconfig import config

class GridPyclientBase(object):
    def __init__(self):
        self.api_client = apiclient.APIClient(api_base_url)
        self.api_client.set_auth_header("Bearer %s" % JWT)