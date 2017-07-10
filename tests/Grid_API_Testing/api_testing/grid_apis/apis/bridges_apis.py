from api_testing.grid_apis.grid_api_base import GridAPIBase


class BridgesAPI(GridAPIBase):
    def __init__(self):
        super().__init__()

    def get_nodes_bridges(self, nodeid):
        method = 'get'
        api = ['nodes', nodeid, 'bridges']
        return self.request_api(method=method, api=api)

    def get_nodes_bridges_bridgeid(self, nodeid, bridgeid):
        method = 'get'
        api = ['nodes', nodeid, 'bridges', bridgeid]
        return self.request_api(method=method, api=api)

    def post_nodes_bridges(self, nodeid, body):
        method = 'post'
        api = ['nodes', nodeid, 'bridges']
        return self.request_api(method=method, api=api, body=body)

    def delete_nodes_bridges_bridgeid(self, nodeid, bridgeid):
        method = 'delete'
        api = ['nodes', nodeid, 'bridges', bridgeid]
        return self.request_api(method=method, api=api)
