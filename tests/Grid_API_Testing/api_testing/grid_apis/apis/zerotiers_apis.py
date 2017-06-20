from api_testing.grid_apis.grid_api_base import GridAPIBase


class ZerotiersAPI(GridAPIBase):
    def __init__(self):
        super().__init__()

    def get_nodes_zerotiers(self, nodeid):
        method = 'get'
        api = ['nodes', nodeid, 'zerotiers']
        return self.request_api(method=method, api=api)

    def get_nodes_zerotiers_zerotierid(self, nodeid, zerotierid):
        method = 'get'
        api = ['nodes', nodeid, 'zerotiers', zerotierid]
        return self.request_api(method=method, api=api)

    def post_nodes_zerotiers(self, nodeid, body):
        method = 'post'
        api = ['nodes', nodeid, 'zerotiers']
        return self.request_api(method=method, api=api, body=body)

    def delete_nodes_zerotiers_zerotierid(self, nodeid, zerotierid):
        method = 'delete'
        api = ['nodes', nodeid, 'zerotiers', zerotierid]
        return self.request_api(method=method, api=api)
