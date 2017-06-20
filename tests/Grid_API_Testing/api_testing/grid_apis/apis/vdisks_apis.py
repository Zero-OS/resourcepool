from api_testing.grid_apis.grid_api_base import GridAPIBase


class VDisksAPIs(GridAPIBase):
    def __init__(self):
        super().__init__()

    def get_vdisks(self):
        method = 'get'
        api = ['vdisks']
        return self.request_api(method=method, api=api)

    def post_vdisks(self, body):
        method = 'post'
        api = ['vdisks']
        return self.request_api(method=method, api=api, body=body)

    def get_vdisks_vdiskid(self, vdiskid):
        method = 'get'
        api = ['vdisks', vdiskid]
        return self.request_api(method=method, api=api)

    def delete_vdisks_vdiskid(self, vdiskid):
        method = 'delete'
        api = ['vdisks', vdiskid]
        return self.request_api(method=method, api=api)

    def post_vdisks_vdiskid_resize(self, vdiskid, body):
        method = 'post'
        api = ['vdisks', vdiskid, 'resize']
        return self.request_api(method=method, api=api, body=body)

    def post_vdisks_vdiskid_rollback(self, vdiskid, body):
        method = 'post'
        api = ['vdisks', vdiskid, 'rollback']
        return self.request_api(method=method, api=api, body=body)
