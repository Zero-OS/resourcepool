from api_testing.grid_apis.grid_api_base import GridAPIBase


class VmsAPI(GridAPIBase):
    def __init__(self):
        super().__init__()

    def get_nodes_vms(self, nodeid):
        method = 'get'
        api = ['nodes', nodeid, 'vms']
        return self.request_api(method=method, api=api)

    def get_nodes_vms_vmid(self, nodeid, vmid):
        method = 'get'
        api = ['nodes', nodeid, 'vms', vmid]
        return self.request_api(method=method, api=api)

    def get_nodes_vms_vmid_info(self, nodeid, vmid):
        method = 'get'
        api = ['nodes', nodeid, 'vms', vmid, 'info']
        return self.request_api(method=method, api=api)

    def post_nodes_vms(self, nodeid, body):
        method = 'post'
        api = ['nodes', nodeid, 'vms']
        return self.request_api(method=method, api=api, body=body)

    def put_nodes_vms_vmid(self, nodeid, vmid, body):
        method = 'put'
        api = ['nodes', nodeid, 'vms', vmid]
        return self.request_api(method=method, api=api, body=body)

    def delete_nodes_vms_vmid(self, nodeid, vmid):
        method = 'delete'
        api = ['nodes', nodeid, 'vms', vmid]
        return self.request_api(method=method, api=api)

    def post_nodes_vms_vmid_start(self, nodeid, vmid):
        method = 'post'
        api = ['nodes', nodeid, 'vms', vmid, 'start']
        return self.request_api(method=method, api=api)

    def post_nodes_vms_vmid_stop(self, nodeid, vmid):
        method = 'post'
        api = ['nodes', nodeid, 'vms', vmid, 'stop']
        return self.request_api(method=method, api=api)

    def post_nodes_vms_vmid_pause(self, nodeid, vmid):
        method = 'post'
        api = ['nodes', nodeid, 'vms', vmid, 'pause']
        return self.request_api(method=method, api=api)

    def post_nodes_vms_vmid_resume(self, nodeid, vmid):
        method = 'post'
        api = ['nodes', nodeid, 'vms', vmid, 'resume']
        return self.request_api(method=method, api=api)

    def post_nodes_vms_vmid_shutdown(self, nodeid, vmid):
        method = 'post'
        api = ['nodes', nodeid, 'vms', vmid, 'shutdown']
        return self.request_api(method=method, api=api)

    def post_nodes_vms_vmid_migrate(self, nodeid, vmid, body):
        method = 'post'
        api = ['nodes', nodeid, 'vms', vmid, 'migrate']
        return self.request_api(method=method, api=api, body=body)
