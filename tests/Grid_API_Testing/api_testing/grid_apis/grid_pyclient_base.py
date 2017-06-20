from zeroos.orchestrator import client as apiclient
from testconfig import config


class GridPyclientBase(object):
    def __init__(self):
        self.config = config['main']
        self.api_base_url = self.config['api_base_url']
        self.api_client = apiclient.APIClient(self.api_base_url)
        