from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase


class ContainersAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_containers(self, nodeid):
        return self.orchestrator_client.nodes.ListContainers(nodeid=nodeid)

    @catch_exception_decoration_return
    def post_containers(self, nodeid, **kwargs):
        data = {"name": self.random_string(),
                "hostname": self.random_string(),
                "flist": "https://hub.gig.tech/gig-official-apps/ubuntu1604.flist",
                "hostNetworking": False,
                "initProcesses": [],
                "filesystems": [],
                "ports": [],
                "nics": [],
                "storage": "ardb://hub.gig.tech:16379"
                }
        data = self.update_default_data(default_data=data, new_data=kwargs)
        response = self.orchestrator_client.nodes.CreateContainer(nodeid=nodeid, data=data)
        return response, data

    @catch_exception_decoration
    def delete_containers_containerid(self, nodeid, containername):
        response = self.orchestrator_client.nodes.DeleteContainer(nodeid=nodeid, containername=containername)
        return response

    @catch_exception_decoration
    def get_containers_containerid(self, nodeid, containername):
        return self.orchestrator_client.nodes.GetContainer(nodeid=nodeid, containername=containername)

    @catch_exception_decoration
    def post_containers_containerid_start(self, nodeid, containername):
        return self.orchestrator_client.nodes.StartContainer(nodeid=nodeid, containername=containername, data={})

    @catch_exception_decoration
    def post_containers_containerid_stop(self, nodeid, containername):
        return self.orchestrator_client.nodes.StopContainer(nodeid=nodeid, containername=containername, data={})

    @catch_exception_decoration
    def post_containers_containerid_filesystem(self, nodeid, containername, data, params):
        return self.orchestrator_client.nodes.FileUpload(nodeid=nodeid, containername=containername, data=data,
                                                         query_params=params)

    @catch_exception_decoration
    def get_containers_containerid_filesystem(self, nodeid, containername, params):
        return self.orchestrator_client.nodes.FileDownload(nodeid=nodeid, containername=containername,
                                                           query_params=params)

    @catch_exception_decoration
    def delete_containers_containerid_filesystem(self, nodeid, containername, data):
        return self.orchestrator_client.nodes.FileDelete(nodeid=nodeid, containername=containername, data=data)

    @catch_exception_decoration
    def get_containers_containerid_jobs(self, nodeid, containername):
        return self.orchestrator_client.nodes.ListContainerJobs(nodeid=nodeid, containername=containername)

    @catch_exception_decoration
    def delete_containers_containerid_jobs(self, nodeid, containername):
        return self.orchestrator_client.nodes.KillAllContainerJobs(nodeid=nodeid, containername=containername)

    @catch_exception_decoration
    def get_containers_containerid_jobs_jobid(self, nodeid, containername, jobid):
        return self.orchestrator_client.nodes.GetContainerJob(nodeid=nodeid, containername=containername, jobid=jobid)

    @catch_exception_decoration
    def post_containers_containerid_jobs_jobid(self, nodeid, containername, jobid, data):
        return self.orchestrator_client.nodes.SendSignalToJob(nodeid=nodeid, containername=containername, jobid=jobid,
                                                              data=data)

    @catch_exception_decoration
    def delete_containers_containerid_jobs_jobid(self, nodeid, containername, jobid):
        return self.orchestrator_client.nodes.KillContainerJob(nodeid=nodeid, containername=containername, jobid=jobid)

    @catch_exception_decoration
    def post_containers_containerid_ping(self, nodeid, containername):
        return self.orchestrator_client.nodes.PingContainer(nodeid=nodeid, containername=containername, data={})

    @catch_exception_decoration
    def get_containers_containerid_state(self, nodeid, containername):
        return self.orchestrator_client.nodes.GetContainerState(nodeid=nodeid, containername=containername)

    @catch_exception_decoration
    def get_containers_containerid_info(self, nodeid, containername):
        return self.orchestrator_client.nodes.GetContainerOSInfo(nodeid=nodeid, containername=containername)

    @catch_exception_decoration
    def get_containers_containerid_processes(self, nodeid, containername):
        return self.orchestrator_client.nodes.ListContainerProcesses(nodeid=nodeid, containername=containername)

    @catch_exception_decoration
    def post_containers_containerid_jobs(self, nodeid, containername, data):
        return self.orchestrator_client.nodes.StartContainerJob(nodeid=nodeid, containername=containername, data=data)

    @catch_exception_decoration
    def get_containers_containerid_processes_processid(self, nodeid, containername, processid):
        return self.orchestrator_client.nodes.GetContainerProcess(nodeid=nodeid, containername=containername,
                                                                  processid=processid)

    @catch_exception_decoration
    def post_containers_containerid_processes_processid(self, nodeid, containername, processid, data):
        return self.orchestrator_client.nodes.SendSignalToProcess(nodeid=nodeid, containername=containername,
                                                                  processid=processid, data=data)

    @catch_exception_decoration
    def delete_containers_containerid_processes_processid(self, nodeid, containername, processid):
        return self.orchestrator_client.nodes.KillContainerProcess(nodeid=nodeid, containername=containername,
                                                                   processid=processid)
