from api_testing.grid_apis.grid_pyclient_base import GridPyclientBase
from requests import HTTPError


class NodesAPI(GridPyclientBase):
    def __init__(self):
        super().__init__()

    def get_nodes(self):
        try:
            response = self.api_client.nodes.ListNodes()
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid(self, node_id):
        try:
            response = self.api_client.nodes.GetNode(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_jobs(self, node_id):
        try:
            response = self.api_client.nodes.ListNodeJobs(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_jobs_jobid(self, node_id, job_id):
        try:
            response = self.api_client.nodes.GetNodeJob(nodeid=node_id, jobid=job_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_nodeid_jobs(self, node_id):
        try:
            response = self.api_client.nodes.KillAllNodeJobs(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_nodeid_jobs_jobid(self, node_id, job_id):
        try:
            response = self.api_client.nodes.KillNodeJob(nodeid=node_id, jobid=job_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_nodeid_ping(self, node_id):
        ###work around
        try:
            response = self.api_client.nodes.PingNode(nodeid=node_id, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_state(self,node_id):
        try:
            response = self.api_client.nodes.GetNodeState(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_nodes_nodeid_reboot(self,node_id):
        ###work around
        try:
            response = self.api_client.nodes.RebootNode(nodeid=node_id, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_cpus(self,node_id):
        try:
            response = self.api_client.nodes.GetCPUInfo(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_disks(self,node_id):
        try:
            response = self.api_client.nodes.GetDiskInfo(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_mem(self,node_id):
        try:
            response = self.api_client.nodes.GetMemInfo(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_nics(self, node_id):
        try:
            response = self.api_client.nodes.GetNicInfo(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_info(self,node_id):
        try:
            response = self.api_client.nodes.GetNodeOSInfo(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_processes(self,node_id):
        try:
            response = self.api_client.nodes.ListNodeProcesses(nodeid=node_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_nodes_nodeid_processes_processid(self, node_id, process_id):
        try:
            response = self.api_client.nodes.GetNodeProcess(nodeid=node_id, processid=process_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_nodes_nodeid_process_processid(self, node_id, process_id):
        try:
            response = self.api_client.nodes.KillNodeProcess(nodeid=node_id, processid=process_id)
        except HTTPError as e:
            response = e.response
        finally:
            return response
