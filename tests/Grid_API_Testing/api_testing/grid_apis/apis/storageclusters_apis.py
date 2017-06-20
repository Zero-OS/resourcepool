from api_testing.grid_apis.grid_api_base import GridAPIBase


class Storageclusters(GridAPIBase):
    def __init__(self):
        super().__init__()

    def post_storageclusters(self, body):
        method = 'post'
        api = ['storageclusters']
        return self.request_api(method=method, api=api, body=body)

    def get_storageclusters(self):
        method = 'get'
        api = ['storageclusters']
        return self.request_api(method=method, api=api)

    def get_storageclusters_label(self, label):
        method = 'get'
        api = ['storageclusters',label]
        return self.request_api(method=method, api=api)

    def delete_storageclusters_label(self, label):
        method = 'delete'
        api = ['storageclusters',label]
        return self.request_api(method=method, api=api)
