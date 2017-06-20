import random
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.grid_apis.pyclient.nodes_apis import NodesAPI
from api_testing.python_client.client import Client
import unittest
import time

class TestNodeidAPI(TestcasesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nodes_api = NodesAPI()

    def setUp(self):
        super(TestNodeidAPI,  self).setUp()

        self.lg.info('Choose one random node of list of running nodes.')
        self.node_id = self.get_random_node()
        if self.node_id is None:
            self.lg.info(' No node found')
            return
        self.node = {}
        for node in self.nodes:
            if node['id'] == self.node_id:
                self.g8os_ip = node['ip']
                self.node = node
                break
        self.python_client = Client(self.g8os_ip)

    def test001_list_nodes(self):
        """ GAT-001
        *GET:/node/ Expected: List of all nodes*

        **Test Scenario:**

        #. Send get nodes api request.
        #. Compare results with golden value.
        """
        self.lg.info('send get nodes api request ')
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare results with golden value.')
        Running_nodes=[]
        Nodes_result = response.json()
        for node in Nodes_result:
            if node['status'] == 'running':
                Running_nodes.append(node)
        self.assertEqual(len(Running_nodes), len(self.nodes))
        for node in Running_nodes:
            node_info = [item for item in self.nodes if item["id"] == node["id"]]
            self.assertEqual(len(node_info),1)
            for key in node.keys():
                if key in node_info[0].keys():
                    self.assertEqual(node[key], node_info[0][key])

    def test002_get_nodes_details(self):
        """ GAT-002
        *GET:/nodes/{nodeid} - Expected: id, status, hostname*

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Send get nodes/{nodeid} api request.
        #. Compare results with golden value.
        """
        self.lg.info(' Send get nodes/{nodeid} api request.')
        response = self.nodes_api.get_nodes_nodeid(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare results with golden value.')
        node_details = response.json()
        for key in self.node.keys():
            if key in node_details.keys():
                self.assertEqual(self.node[key], node_details[key])

    def test003_list_jobs(self):
        """ GAT-003
        *GET:/nodes/{nodeid}/jobs - Expected: job list items*

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Send get /nodes/{nodeid}/jobs api request.
        #. Compare results with golden value.
        """
        self.lg.info('Send get /nodes/{nodeid}/jobs api request.')
        response = self.nodes_api.get_nodes_nodeid_jobs(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare results with golden value.')
        jobs = response.json()
        client_jobs = self.python_client.get_jobs_list()
        self.assertEqual(len(jobs), len(client_jobs))
        for job in jobs:
            for client_job in client_jobs:
                if job['id'] == client_job['id']:
                    self.assertEqual(job['startTime'], client_job['starttime'])
                    break

    def test004_kill_jobs(self):
        """ GAT-004
        *DELETE:/nodes/{nodeid}/jobs *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Send get /nodes/{nodeid}/jobs api request.
        #. Check that all jobs has been killed.
        """
        self.lg.info(' Send get /nodes/{nodeid}/jobs api request.')
        response = self.nodes_api.delete_nodes_nodeid_jobs(node_id=self.node_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that all jobs has been killed.')
        response = self.nodes_api.get_nodes_nodeid_jobs(node_id=self.node_id)
        jobs_list = response.json()
        self.assertEqual(len(jobs_list),3)

    def test005_get_job_details(self):
        """ GAT-005
        *GET:/nodes/{nodeid}/jobs/{jobid} *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Get list of jobs of this node .
        #. Choose one of these jobs to list its details.
        #. Send get /nodes/{nodeid}/jobs/{jobid} api request.
        #. Compare response with the golden values.
        """
        self.lg.info('Get list of jobs of this node .')
        response = self.nodes_api.get_nodes_nodeid_jobs(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('Choose one of these jobs to list its details.')
        jobs_list = response.json()
        job_id = jobs_list[random.randint(0, (len(jobs_list)-1))]['id']

        self.lg.info('Send get /nodes/{nodeid}/jobs/{jobid} api request.')
        response = self.nodes_api.get_nodes_nodeid_jobs_jobid(node_id=self.node_id, job_id=job_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare response with the golden values.')
        job_details = response.json()
        client_jobs = self.python_client.get_jobs_list()
        for client_job in client_jobs:
            if client_job['id'] == job_id:
                for key in job_details.keys():
                    if key in client_job.keys():
                        self.assertEqual(job_details[key], client_job[key])
                break

    def test006_kill_specific_job(self):
        """ GAT-006
        *DELETE:/nodes/{nodeid}/jobs/{jobid} *

        **Test Scenario:**

        #. Start new job .
        #. delete /nodes/{nodeid}/jobs/{jobid} api.
        #. verify this job has been killed.
        """
        self.lg.info('start new job ')
        job_id = self.python_client.start_job()
        self.assertTrue(job_id)

        self.lg.info(' delete /nodes/{nodeid}/jobs/{jobid} api.')
        response = self.nodes_api.delete_nodes_nodeid_jobs_jobid(node_id=self.node_id, job_id=job_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info("verify this job has been killed.")
        jobs = self.python_client.get_jobs_list()
        self.assertFalse(any(job['id'] == job_id for job in jobs))

    def test007_ping_specific_node(self):
        """ GAT-007
        *POST:/nodes/{nodeid}/ping *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Post /nodes/{nodeid}/ping api.
        #. Check response status code.
        """
        self.lg.info('post /nodes/{nodeid}/ping api.')
        response = self.nodes_api.post_nodes_nodeid_ping(node_id=self.node_id)

        self.lg.info('check response status code.')
        self.assertEqual(response.status_code, 200)

    def test008_get_node_state(self):
        """ GAT-008
        *GET:/nodes/{nodeid}/state *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Get /nodes/{nodeid}/state api.
        #. Compare response data with the golden values.
        """
        self.lg.info(' get /nodes/{nodeid}/state api.')
        response = self.nodes_api.get_nodes_nodeid_state(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare response data with the golden values.')
        client_state = self.python_client.get_node_state()
        node_state = response.json()
        for key in node_state.keys():
            if key in client_state.keys():
                self.assertAlmostEqual(node_state[key],
                                       client_state[key],
                                       delta=6000000,msg='different value for key%s'%key)

    @unittest.skip("https://github.com/zero-os/0-core/issues/125, wontfix")
    def test009_reboot_node(self):
        """ GAT-009
        *POST:/nodes/{nodeid}/reboot *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. post /nodes/{nodeid}/reboot api.
        #. verify that this node has been rebooted.
        #. Ping node should succeed
        """
        self.lg.info('post /nodes/{nodeid}/reboot api.')
        response = self.nodes_api.post_nodes_nodeid_reboot(node_id=self.node_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info('verify that this node has been rebooted.')
        content = response.json()
        self.assertEqual(content, 'Machine reboot signal sent successfully')

    def test010_get_cpus_details(self):
        """ GAT-010
        *GET:/nodes/{nodeid}/cpus *

        **Test Scenario:**

        #. Choose one random node from list of running nodes.
        #. get /nodes/{nodeid}/cpus api.
        #. compare response data with the golden values.

        """
        self.lg.info('get /nodes/{nodeid}/cpus api.')
        response = self.nodes_api.get_nodes_nodeid_cpus(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('compare response data with the golden values.')
        result = self.python_client.get_nodes_cpus()
        cpus_info = response.json()
        for i, cpu_info in enumerate(cpus_info):
            for key in cpu_info.keys():
                if key in result[i].keys():
                    if key != 'cores' and key != 'mhz':
                        self.assertEqual(cpu_info[key], result[i][key], "different cpu info for key %s"%key)


    def test011_get_disks_details(self):
        """ GAT-011
        *GET:/nodes/{nodeid}/disks *

        **Test Scenario:**

        #. Choose one random node from list of running nodes.
        #. Get /nodes/{nodeid}/disks api.
        #. Compare response data with the golden values.
        """
        self.lg.info('get /nodes/{nodeid}/disks api.')
        response = self.nodes_api.get_nodes_nodeid_disks(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)
        disks_info = response.json()
        self.lg.info('compare response data with the golden values.')
        result = self.python_client.get_nodes_disks()
        self.assertEqual(result, disks_info)

    def test012_get_memmory_details(self):
        """ GAT-012
        *GET:/nodes/{nodeid}/mem *

        **Test Scenario:**

        #. Choose one random node from list of running nodes.
        #. get /nodes/{nodeid}/mem api.
        #. compare response data with the golden values.
        """
        self.lg.info('get /nodes/{nodeid}/mem api.')
        response = self.nodes_api.get_nodes_nodeid_mem(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('compare response data with the golden values.')
        result = self.python_client.get_nodes_mem()
        memory_info = response.json()
        for key in memory_info.keys():
            if key in result.keys():
                self.assertAlmostEqual(memory_info[key], result[key],
                                       msg="different keys%s"%key,
                                        delta=10000000)

    def test013_get_nics_details(self):
        """ GAT-013
        *GET:/nodes/{nodeid}/nics - network interface information*

        **Test Scenario:**

        #. Choose one random node from list of running nodes.
        #. Get /nodes/{nodeid}/nics api.
        #. compare response data with the golden values.
        """
        self.lg.info('get /nodes/{nodeid}/nics api.')
        response = self.nodes_api.get_nodes_nodeid_nics(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('compare response data with the golden values.')
        golden_result = self.python_client.get_nodes_nics()
        nics_info = response.json()
        self.assertEqual(len(nics_info), len(golden_result))
        for nic_info in nics_info:
            for nic_result in golden_result :
                if nic_result['name']== nic_info['name']:
                    for key in nic_info.keys():
                        if key in nic_result.keys():
                            self.assertEqual(nic_info[key], nic_result[key],
                                             'different value for key %s'%key)
                            break

    def test014_get_os_info_details(self):
        """ GAT-014
        *GET:/nodes/{nodeid}/info - os information*

        **Test Scenario:**

        #. Choose one random node from list of running nodes.
        #. Get /nodes/{nodeid}/info api.
        #. ompare response data with the golden values.
        """
        self.lg.info('Get /nodes/{nodeid}/info api.')
        response = self.nodes_api.get_nodes_nodeid_info(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('compare response data with the golden values.')
        result = self.python_client.get_nodes_info()
        node_info = response.json()
        for key in node_info.keys():
            if key in result.keys():
                self.assertEqual(node_info[key],result[key])

    def test015_list_processes(self):
        """ GAT-015
        *GET:/nodes/{nodeid}/process *

        **Test Scenario:**

        #. Choose one random node from list of running nodes.
        #. get /nodes/{nodeid}/processes api.
        #. compare response data with the golden values.
        """
        self.lg.info('Get /nodes/{nodeid}/process api.')
        response = self.nodes_api.get_nodes_nodeid_processes(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)

        self.lg.info('compare response data with the golden values.')
        processes = {}
        client_processes={}
        client_result = self.python_client.get_processes_list()
        for process in client_result:
            client_processes[process['pid']]=process

        for process in response.json():
            processes[process['pid']]= process
        skip_keys = ['cpu', 'vms', 'rss']
        for process_id in processes.keys():
            process_info = processes[process_id]
            for info in process_info.keys():
                if info not in skip_keys:
                    if info in client_processes[process_id].keys():
                        self.assertEqual(process_info[info],
                                         client_processes[process_id][info],
                                         "different value with key%s"%info)

    def test016_get_process_details(self):
        """ GAT-016
        *GET:/nodes/{nodeid}/processes/{processid} *

        **Test Scenario:**

        #. Choose one random node from list of running nodes.
        #. Get list of running processes
        #. choose one of them.
        #. Get /nodes/{nodeid}/processes/{processid} api.
        #. compare response data with the golden values.

        """
        self.lg.info('Get list of running processes')
        response = self.nodes_api.get_nodes_nodeid_processes(node_id=self.node_id)
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()

        self.lg.info('Choose one of these processes to list its details.')
        process_id = processes_list[random.randint(0, len(processes_list)-1)]['pid']

        self.lg.info('Get /nodes/{nodeid}/process/{processid} api.')
        response = self.nodes_api.get_nodes_nodeid_processes_processid(node_id=self.node_id, process_id=str(process_id))
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare response data with the golden values.')
        process_info = response.json()
        client_result = self.python_client.get_processes_list()
        for process in client_result:
            if process['pid'] == process_info['pid']:
                for info in process_info.keys():
                    if info != 'cpu':
                        if info in process.keys():
                            self.assertEqual(process_info[info], process[info],
                                            "different value with key%s"%info)
                break

    def test017_delete_process(self):
        """ GAT-017
        *DELETE:/nodes/{nodeid}/processes/{processid} *

        **Test Scenario:**

        #. Start new process.
        #. Delete /nodes/{nodeid}/processes/{processid} api.
        #. Make sure that this process has been killed.

        """
        self.lg.info('Start new process.')
        process_id = self.python_client.start_process()
        self.assertTrue(process_id)

        self.lg.info('delete /nodes/{nodeid}/processes/{processid} api.')
        response = self.nodes_api.delete_nodes_nodeid_process_processid(node_id=self.node_id,
                                                                        process_id=str(process_id))
        self.assertEqual(response.status_code, 204)

        self.lg.info('Make sure that this process has been killed.')
        client_processes = self.python_client.get_processes_list()
        self.assertFalse(any(process['pid']== process_id for process in client_processes))
