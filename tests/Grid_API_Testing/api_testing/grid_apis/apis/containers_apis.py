from api_testing.grid_apis.grid_api_base import GridAPIBase


class ContainersAPI(GridAPIBase):
    def __init__(self):
        super().__init__()

    def get_containers(self, node_id):
        method = 'get'
        api = ['nodes', node_id, 'containers']
        return self.request_api(method=method,
                                api=api)
    def post_containers(self, node_id, body):
        method = 'post'
        api = ['nodes', node_id, 'containers']
        return self.request_api(method=method,
                                api=api, body=body)

    def delete_containers_containerid(self, node_id, container_id):
        method = 'delete'
        api = ['nodes', node_id, 'containers', container_id]
        return self.request_api(method=method,
                                api=api)

    def get_containers_containerid(self, node_id, container_id):
        method = 'get'
        api = ['nodes', node_id, 'containers', container_id]
        return self.request_api(method=method,
                                api=api)

    def post_containers_containerid_start(self, node_id, container_id):
        method = 'post'
        api = ['nodes', node_id, 'containers', container_id, 'start']
        return self.request_api(method=method,
                                api=api)
    def post_containers_containerid_stop(self, node_id, container_id):
        method = 'post'
        api = ['nodes', node_id, 'containers', container_id, 'stop']
        return self.request_api(method=method,
                                api=api)

    def post_containers_containerid_filesystem(self, node_id, container_id, body,params):
        method = 'post'
        headers = ""
        api = ['nodes', node_id, 'containers', container_id, 'filesystem']
        api = self.build_api(api)
        return self.requests.post(url=api, headers=headers, files=body, params = params)

    def get_containers_containerid_filesystem(self, node_id, container_id, params):
        method = 'get'
        headers = {'content-type': 'application/octet-stream'}
        api = ['nodes', node_id, 'containers', container_id, 'filesystem']
        return self.request_api(method=method, api=api, params=params)

    def delete_containers_containerid_filesystem(self, node_id, container_id, body):
        method = 'delete'
        api = ['nodes', node_id, 'containers', container_id, 'filesystem']
        return self.request_api(method=method,
                                api=api, body=body)

    def get_containers_containerid_jobs(self, node_id, container_id):
        method = 'get'
        api = ['nodes', node_id, 'containers', container_id, 'jobs']
        return self.request_api(method=method,
                                api=api)

    def post_containers_containerid_jobs(self, node_id, container_id):
        method = 'post'
        api = ['nodes', node_id, 'containers', container_id, 'jobs']
        return self.request_api(method=method,
                                api=api)

    def delete_containers_containerid_jobs(self, node_id, container_id):
        method = 'delete'
        api = ['nodes', node_id, 'containers', container_id, 'jobs']
        return self.request_api(method=method,
                                api=api)

    def get_containers_containerid_jobs_jobid(self, node_id, container_id, job_id):
        method = 'get'
        api = ['nodes', node_id, 'containers', container_id, 'jobs', job_id]
        return self.request_api(method=method,
                                api=api)

    def post_containers_containerid_jobs_jobid(self, node_id, container_id, job_id ,body):
        method = 'post'
        api = ['nodes', node_id, 'containers', container_id, 'jobs', job_id]
        return self.request_api(method=method,
                                api=api, body=body)

    def delete_containers_containerid_jobs_jobid(self, node_id, container_id, job_id):
        method = 'delete'
        api = ['nodes', node_id, 'containers', container_id, 'jobs', job_id]
        return self.request_api(method=method,
                                api=api)
    def post_containers_containerid_ping(self, node_id, container_id):
        method = 'post'
        api = ['nodes', node_id, 'containers', container_id, 'ping']
        return self.request_api(method=method,
                                api=api)
    def get_containers_containerid_state(self, node_id, container_id):
        method = 'get'
        api = ['nodes', node_id, 'containers', container_id, 'state']
        return self.request_api(method=method,
                                api=api)

    def get_containers_containerid_info(self, node_id, container_id):
        method = 'get'
        api = ['nodes', node_id, 'containers', container_id, 'info']
        return self.request_api(method=method,
                                api=api)

    def get_containers_containerid_processes(self, node_id, container_id):
        method = 'get'
        api = ['nodes', node_id, 'containers', container_id, 'processes']
        return self.request_api(method=method,
                                api=api)

    def post_containers_containerid_processes(self, node_id, container_id, body):
        method = 'post'
        api = ['nodes', node_id, 'containers', container_id, 'processes']
        return self.request_api(method=method,
                                api=api, body=body)

    def get_containers_containerid_processes_processid(self, node_id, container_id, processid):
        method = 'get'
        api = ['nodes', node_id, 'containers', container_id, 'processes',processid]
        return self.request_api(method=method,
                                api=api)

    def post_containers_containerid_processes_processid(self, node_id, container_id, processid,body):
        method = 'post'
        api = ['nodes', node_id, 'containers', container_id, 'processes',processid]
        return self.request_api(method=method,
                                api=api, body=body)

    def delete_containers_containerid_processes_processid(self, node_id, container_id, processid):
        method = 'delete'
        api = ['nodes', node_id, 'containers', container_id, 'processes',processid]
        return self.request_api(method=method,
                                api=api)
