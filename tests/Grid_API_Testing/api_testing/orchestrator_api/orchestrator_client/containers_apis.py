from api_testing.orchestrator_api.orchestrator_base import GridPyclientBase
from requests import HTTPError


class ContainersAPI(GridPyclientBase):
    def __init__(self):
        super().__init__()
        self.createdcontainer = []

    def get_containers(self, nodeid):
        try:
            response = self.api_client.nodes.ListContainers(nodeid=nodeid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers(self, nodeid, data):
        try:
            response = self.api_client.nodes.CreateContainer(nodeid=nodeid, data=data)
            if response.status_code == 201:
                self.createdcontainer.append({"node": nodeid, "name": data["name"]})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_containers_containerid(self, nodeid, containername):
        try:
            response = self.api_client.nodes.DeleteContainer(nodeid=nodeid, containername=containername)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid(self, nodeid, containername):
        try:
            response = self.api_client.nodes.GetContainer(nodeid=nodeid, containername=containername)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers_containerid_start(self, nodeid, containername):
        # work around
        try:
            response = self.api_client.nodes.StartContainer(nodeid=nodeid, containername=containername, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers_containerid_stop(self, nodeid, containername):
        # work around
        try:
            response = self.api_client.nodes.StopContainer(nodeid=nodeid, containername=containername, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers_containerid_filesystem(self, nodeid, containername, data, params):
        try:
            response = self.api_client.nodes.FileUpload(nodeid=nodeid, containername=containername, data=data, query_params=params)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid_filesystem(self, nodeid, containername, params):
        try:
            response = self.api_client.nodes.FileDownload(nodeid=nodeid, containername=containername, query_params=params)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    ### https://github.com/Jumpscale/go-raml/issues/280
    def delete_containers_containerid_filesystem(self, nodeid, containername, data):
        try:
            response = self.api_client.nodes.FileDelete(nodeid=nodeid, containername=containername, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid_jobs(self, nodeid, containername):
        try:
            response = self.api_client.nodes.ListContainerJobs(nodeid=nodeid, containername=containername)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_containers_containerid_jobs(self, nodeid, containername):
        try:
            response = self.api_client.nodes.KillAllContainerJobs(nodeid=nodeid, containername=containername)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid_jobs_jobid(self, nodeid, containername, jobid):
        try:
            response = self.api_client.nodes.GetContainerJob(nodeid=nodeid, containername=containername, jobid=jobid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers_containerid_jobs_jobid(self, nodeid, containername, jobid ,data):
        try:
            response = self.api_client.nodes.SendSignalToJob(nodeid=nodeid, containername=containername, jobid=jobid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_containers_containerid_jobs_jobid(self, nodeid, containername, jobid):
        try:
            response = self.api_client.nodes.KillContainerJob(nodeid=nodeid, containername=containername, jobid=jobid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers_containerid_ping(self, nodeid, containername):
        try:
            response = self.api_client.nodes.PingContainer(nodeid=nodeid, containername=containername, data={})
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid_state(self, nodeid, containername):
        try:
            response = self.api_client.nodes.GetContainerState(nodeid=nodeid, containername=containername)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid_info(self, nodeid, containername):
        try:
            response = self.api_client.nodes.GetContainerOSInfo(nodeid=nodeid, containername=containername)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid_processes(self, nodeid, containername):
        try:
            response = self.api_client.nodes.ListContainerProcesses(nodeid=nodeid, containername=containername)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers_containerid_jobs(self, nodeid, containername, data):
        try:
            response = self.api_client.nodes.StartContainerJob(nodeid=nodeid, containername=containername, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def get_containers_containerid_processes_processid(self, nodeid, containername, processid):
        try:
            response = self.api_client.nodes.GetContainerProcess(nodeid=nodeid, containername=containername, processid=processid)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def post_containers_containerid_processes_processid(self, nodeid, containername, processid, data):
        try:
            response = self.api_client.nodes.SendSignalToProcess(nodeid=nodeid, containername=containername, processid=processid, data=data)
        except HTTPError as e:
            response = e.response
        finally:
            return response

    def delete_containers_containerid_processes_processid(self, nodeid, containername, processid):
        try:
            response = self.api_client.nodes.KillContainerProcess(nodeid=nodeid, containername=containername, processid=processid)
        except HTTPError as e:
            response = e.response
        finally:
            return response
