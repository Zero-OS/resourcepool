from framework.orchestrator_apis import *


class NodesAPI:
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def get_nodes(self):
        return self.orchestrator_client.nodes.ListNodes()

    @catch_exception_decoration
    def get_nodes_nodeid(self, node_id):
        return self.orchestrator_client.nodes.GetNode(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_jobs(self, node_id):
        return self.orchestrator_client.nodes.ListNodeJobs(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_jobs_jobid(self, node_id, job_id):
        return self.orchestrator_client.nodes.GetNodeJob(nodeid=node_id, jobid=job_id)

    @catch_exception_decoration
    def delete_nodes_nodeid_jobs(self, node_id):
        return self.orchestrator_client.nodes.KillAllNodeJobs(nodeid=node_id)

    @catch_exception_decoration
    def delete_nodes_nodeid_jobs_jobid(self, node_id, job_id):
        return self.orchestrator_client.nodes.KillNodeJob(nodeid=node_id, jobid=job_id)

    @catch_exception_decoration
    def post_nodes_nodeid_ping(self, node_id):
        return self.orchestrator_client.nodes.PingNode(nodeid=node_id, data={})

    @catch_exception_decoration
    def get_nodes_nodeid_state(self, node_id):
        return self.orchestrator_client.nodes.GetNodeState(nodeid=node_id)

    @catch_exception_decoration
    def post_nodes_nodeid_reboot(self, node_id):
        return self.orchestrator_client.nodes.RebootNode(nodeid=node_id, data={})

    @catch_exception_decoration
    def get_nodes_nodeid_cpus(self, node_id):
        return self.orchestrator_client.nodes.GetCPUInfo(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_disks(self, node_id):
        return self.orchestrator_client.nodes.GetDiskInfo(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_mem(self, node_id):
        return self.orchestrator_client.nodes.GetMemInfo(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_nics(self, node_id):
        return self.orchestrator_client.nodes.GetNicInfo(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_info(self, node_id):
        return self.orchestrator_client.nodes.GetNodeOSInfo(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_processes(self, node_id):
        return self.orchestrator_client.nodes.ListNodeProcesses(nodeid=node_id)

    @catch_exception_decoration
    def get_nodes_nodeid_processes_processid(self, node_id, process_id):
        return self.orchestrator_client.nodes.GetNodeProcess(nodeid=node_id, processid=process_id)

    @catch_exception_decoration
    def delete_nodes_nodeid_process_processid(self, node_id, process_id):
        return self.orchestrator_client.nodes.KillNodeProcess(nodeid=node_id, processid=process_id)
