import random
import time
import unittest
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.utiles.core0_client import Client
from api_testing.grid_apis.orchestrator_client.containers_apis import ContainersAPI


class TestcontaineridAPI(TestcasesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.containers_api = ContainersAPI()

    def setUp(self):
        super(TestcontaineridAPI,  self).setUp()

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
        self.g8core = Client(self.g8os_ip, password=self.jwt)

        self.root_url = "https://hub.gig.tech/gig-official-apps/ubuntu1604.flist"
        self.storage = "ardb://hub.gig.tech:16379"
        self.container_name = self.rand_str()
        self.hostname = self.rand_str()
        self.job_body = {'name': 'yes'}
        self.container_body = {"name": self.container_name, "hostname": self.hostname, "flist": self.root_url,
                               "hostNetworking": False, "initProcesses": [], "filesystems": [],
                               "ports": [], "storage": self.storage
                               }

    def tearDown(self):
        self.lg.info('TearDown:delete all created container ')
        for container in self.createdcontainer:
            self.containers_api.delete_containers_containerid(container['node'],
                                                              container['container'])

    def test001_list_containers(self):
        """ GAT-022
        *GET:/node/{nodeid}/containers Expected: List of all running containers *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Send get nodes/{nodeid}/containers api request.
        #. Compare results with golden value.
        """
        containers_id = []
        Running_containers_list= []
        self.lg.info('Send get nodes/{nodeid}/containers api request.')
        response = self.containers_api.get_containers(self.node_id)
        self.assertEqual(response.status_code, 200)
        self.lg.info('Compare results with golden value.')
        containers_list = response.json()
        for container in containers_list:
            if container['status']=="running":
                Running_containers_list.append(container)
        golden_value_list = self.g8core.client.container.list()
        self.assertEqual(len(Running_containers_list), len(golden_value_list))
        for container in Running_containers_list:
            if container['name']:
                self.assertTrue(self.g8core.client.container.find(container['name']),'container %s not in golden value '%container['name'])

    def test002_create_containers(self):
        """ GAT-023
        *post:/node/{nodeid}/containers Expected: create container then delete it *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Send post nodes/{nodeid}/containers api request.
        #. Make sure it created with required values, should succeed.
        #. Delete ctreated container,should succeed
        #. make sure that it deleted .
        """

        self.lg.info('Send post nodes/{nodeid}/containers api request.')
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('Make sure it created with required values, should succeed.')
        self.assertEqual(response.headers['Location'], "/nodes/%s/containers/%s" % (self.node_id, self.container_name))
        response = self.containers_api.get_containers_containerid(self.node_id, self.container_name)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        for key in response_data.keys():
            if key == 'initprocesses':
                self.assertEqual(response_data[key], self.container_body['initProcesses'])
                continue
            if key in self.container_body.keys():
                self.assertEqual(response_data[key], self.container_body[key])

        self.lg.info('delete created container')
        response = self.containers_api.delete_containers_containerid(self.node_id, self.container_name)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Make sure that it deleted ')
        response = self.containers_api.get_containers(self.node_id)
        containers_list = response.json()
        self.assertFalse(any(container['name'] == self.container_name for container in containers_list))
        self.assertFalse(self.g8core.client.container.find(self.container_name),'container %s still exist in g8os '%self.container_name)


    def test003_get_container_details(self):
        """ GAT-024
        *get:/node/{nodeid}/containers/containerid Expected: get container details *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Get:/node/{nodeid}/containers/containerid
        #. Compare results with golden value.

        """
        self.lg.info('Choose random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Send get nodes/{nodeid}/containers/containerid api request.')
        response = self.containers_api.get_containers_containerid(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.lg.info(' Compare results with golden value.')
        golden_value = self.g8core.get_container_info(container_name)
        self.assertTrue(golden_value)
        for key in data.keys():
            if key in golden_value.keys():
                self.assertEqual(data[key], golden_value[key])

    def test004_stop_and_start_container(self):
        """ GAT-025
        *post:/node/{nodeid}/containers/containerid/start Expected: get container details *

        **Test Scenario:**

        #. Create container.
        #. post:/node/{nodeid}/containers/containerid/stop.
        #. Check that container stpoed .
        #. Post:/node/{nodeid}/containers/containerid/start.
        #. Check that container running .

        """
        self.lg.info('Create container ')
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})
        self.assertTrue(container_id)
        self.lg.info('post:/node/{nodeid}/containers/containerid/stop.')

        response = self.containers_api.post_containers_containerid_stop(self.node_id, self.container_name)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that container stoped.')
        self.assertTrue(self.g8core.wait_on_container_update(container_id, 60, True))

        self.lg.info('post:/node/{nodeid}/containers/containerid/start.')
        response = self.containers_api.post_containers_containerid_start(self.node_id, self.container_name)
        self.assertEqual(response.status_code, 201)

        self.lg.info('Check that container running.')
        self.assertTrue(self.g8core.wait_on_container_update(self.container_name, 60, False))

    def test005_get_running_jobs(self):
        """ GAT-026
        *get:/node/{nodeid}/containers/containerid/jobs Expected: get container details *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Get:/node/{nodeid}/containers/containerid/jobs
        #. Compare results with golden value.

        """
        self.lg.info('Choose random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Send get nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.get_containers_containerid_jobs(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare results with golden value.')
        running_jobs_list = response.json()
        golden_values = self.g8core.get_container_job_list(container_name)

        api_jobs = set([(job['id'], job['startTime'])for job in running_jobs_list])
        self.assertEqual(len(golden_values.difference(api_jobs)), 1)

    def test006_post_new_job_in_container(self):
        """ GAT-027
        *post:/node/{nodeid}/containers/containerid/jobs *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Send post nodes/{nodeid}/containers/containerid/jobs request.
        #. Check that you can get created job.

        """
        job_name = self.job_body['name']
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                             self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name, job_id,100, False))

        self.lg.info('Check that you can get created job.')
        time.sleep(7)
        response = self.containers_api.get_containers_containerid_jobs_jobid(self.node_id, container_name, job_id)
        self.assertEqual(response.status_code, 200)

    def test007_kill_all_running_jobs(self):
        """ GAT-028
        *get:/node/{nodeid}/containers/containerid/jobs Expected: get container details*

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. delete :/node/{nodeid}/containers/containerid/jobs.
        #. Check that all jobs in this container killed.
        #. Compare results with golden value.

        """
        self.lg.info('Choose random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Spawn multiple jobs.')
        for i in range(0, 3):
            response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                            self.job_body)
            self.assertEqual(response.status_code, 202)
            job_id = response.headers['Location'].split('/')[6]
            self.assertTrue(self.g8core.wait_on_container_job_update(container_name, job_id, 15, False))

        self.lg.info('Send delete nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.delete_containers_containerid_jobs(self.node_id, container_name)
        self.assertEqual(response.status_code, 204)
        time.sleep(5)

        self.lg.info('Check that all jobs in this container killed ')
        response = self.containers_api.get_containers_containerid_jobs(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        jobs_list = response.json()
        self.assertEqual(len(jobs_list), 1)
        self.assertEqual(len(self.g8core.get_container_job_list(container_name)), 1)

        self.lg.info('Compare results with golden value.')

    def test008_get_job_in_container_details(self):
        """ GAT-029
        *get:/node/{nodeid}/containers/containerid/jobs/jobid Expected: get container details *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Choose one random job of list of running jobs in  container.
        #. Send get nodes/{nodeid}/containers/containerid/jobs/jobid api request
        #. Compare results with golden value.

        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info(' spawn job in container ')
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                             self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name, job_id, 100, False))

        self.lg.info('Send get nodes/{nodeid}/containers/containerid/jobs/jobid api request.')
        response = self.containers_api.get_containers_containerid_jobs_jobid(self.node_id, container_name, job_id)
        self.assertEqual(response.status_code, 200)
        job_details = response.json()

        self.lg.info('Compare results with golden value.')
        container_id = int(list(self.g8core.client.container.find(container_name).keys())[0])
        container = self.g8core.client.container.client(container_id)
        golden_value = container.job.list(job_id)[0]
        self.assertEqual(golden_value['cmd']['command'], job_details['name'])
        self.assertEqual(golden_value['cmd']['id'], job_details['id'])
        self.assertEqual(golden_value['starttime'], job_details['startTime'])

        response = self.containers_api.delete_containers_containerid_jobs_jobid(self.node_id, container_name, job_id)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name, job_id, 100, True))

    def test009_post_signal_job_in_container_details(self):
        """ GAT-030
        *get:/node/{nodeid}/containers/containerid/jobs/jobid Expected: get container details *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Choose one random job of list of running jobs in  container.
        #. Send post nodes/{nodeid}/containers/containerid/jobs/jobid api request, should succeed

        """
        signal = random.randint(1, 30)
        body = {'signal': signal}
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info(' spawn job in container ')
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/jobs/jobid api request.')
        response = self.containers_api.post_containers_containerid_jobs_jobid(self.node_id, container_name,
                                                                              job_id, body)
        self.assertEqual(response.status_code, 204)


    def test010_kill_specific_job(self):
        """ GAT-031
        *get:/node/{nodeid}/containers/containerid/jobs/jobid Expected: get container details *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Choose one random job of list of running jobs in  container.
        #. Send delete nodes/{nodeid}/containers/containerid/jobs/jobid api request, should succeed
        #. Check that job delted from running jobs list.
        #. Check that job delted from client list.
        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info(' spawn job in container ')
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name,
                                                                 job_id, 60, False))

        self.lg.info('Send delete  nodes/{nodeid}/containers/containerid/jobs/jobid api request.')
        response = self.containers_api.delete_containers_containerid_jobs_jobid(self.node_id, container_name, job_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that job delted from running jobs list.')
        response = self.containers_api.get_containers_containerid_jobs(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        running_jobs_list = response.json()
        for job in running_jobs_list:
            self.assertNotEqual(job['id'], job_id)

        self.lg.info('Check that job delted from client list.')
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name,
                                                             job_id, 60, True))

    def test011_post_ping_to_container(self):
        """ GAT-032
        *get:/node/{nodeid}/containers/containerid/ping *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Send post nodes/{nodeid}/containers/containerid/post request.

        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/ping api request.')
        response = self.containers_api.post_containers_containerid_ping(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)

    def test012_get_state_of_container(self):
        """ GAT-033
        *get:/node/{nodeid}/containers/containerid/state *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Send get nodes/{nodeid}/containers/containerid/state request.
        #. Compare results with golden value.

        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Send GET  nodes/{nodeid}/containers/containerid/state api request.')
        response = self.containers_api.get_containers_containerid_state(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)

        self.lg.info(' Compare results with golden value.')
        container_state = response.json()
        container_id = int(list(self.g8core.client.container.find(container_name).keys())[0])
        golden_value = self.g8core.client.container.list()[str(container_id)]
        self.assertEqual(golden_value['swap'], container_state['swap'])

    def test013_get_info_of_container_os(self):
        """ GAT-034
        *get:/node/{nodeid}/containers/containerid/info *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Send get nodes/{nodeid}/containers/containerid/info request.
        #. Compare results with golden value.

        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/state api request.')
        response = self.containers_api.get_containers_containerid_info(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)

        self.lg.info(' Compare results with golden value.')
        container_info = response.json()
        container_id = int(list(self.g8core.client.container.find(container_name).keys())[0])
        container = self.g8core.client.container.client(container_id)
        golden_value = container.info.os()
        self.assertAlmostEqual(golden_value.pop('uptime'), container_info.pop('uptime'), delta=50)
        for key in container_info:
            if key not in golden_value:
                self.assertEqual(golden_value[key], container_info[key])

    def test014_get_running_processes_in_container(self):
        """ GAT-035
        *get:/node/{nodeid}/containers/containerid/processes *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Send get nodes/{nodeid}/containers/containerid/processes request.
        #. Compare results with golden value.

        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/state api request.')
        response = self.containers_api.get_containers_containerid_processes(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        processes = response.json()
        container_id = int(list(self.g8core.client.container.find(container_name).keys())[0])
        container = self.g8core.client.container.client(container_id)
        golden_values = container.process.list()

        self.lg.info(' Compare results with golden value.')
        processes.sort(key=lambda d: d['pid'])
        golden_values.sort(key=lambda d: d['pid'])
        for i, p in enumerate(processes):
            self.assertEqual(p['cmdline'], golden_values[i]['cmdline'])
            self.assertEqual(p['pid'], golden_values[i]['pid'])
            self.assertEqual(p['swap'], golden_values[i]['swap'])

    def test015_get_process_details_in_container(self):
        """ GAT-036
        *post:/node/{nodeid}/containers/containerid/processes/processid *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Choose one random process of list of process.
        #. Send get nodes/{nodeid}/containers/containerid/processes/processid request.
        #. Compare results with golden value.

        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Choose one random process of list of process.')
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name, job_id, 100, False))

        response = self.containers_api.get_containers_containerid_processes(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        process_id = None
        while not process_id or process_id == 1:
            random_number = random.randint(0, len(processes_list)-1)
            process_id = processes_list[random_number]['pid']

        self.lg.info('Send get  nodes/{nodeid}/containers/containerid/processes/processid api request.')
        response = self.containers_api.get_containers_containerid_processes_processid(self.node_id, container_name,
                                                                                      str(process_id))
        self.assertEqual(response.status_code, 200)
        process = response.json()
        container_id = int(list(self.g8core.client.container.find(container_name).keys())[0])
        container = self.g8core.client.container.client(container_id)
        golden_value = container.process.list(process_id)[0]

        self.lg.info(' Compare results with golden value.')
        skip_keys = ['cpu', 'vms', 'rss']
        for key in process:
            if key in skip_keys:
                continue
            if key in golden_value.keys():
                self.assertEqual(golden_value[key], process[key])

    def test016_delete_process_in_container(self):
        """ GAT-037
        *post:/node/{nodeid}/containers/containerid/processes/processid *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Choose one random process of list of process.
        #. Send delete nodes/{nodeid}/containers/containerid/processes/processid request.
        #. Check that created process deleted from process list.
        #. Compare results with golden value.

        """
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)

        self.lg.info('Choose one random process of list of processes')
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                        self.job_body)

        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name, job_id, 100, False))
        response = self.containers_api.get_containers_containerid_processes(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        process_id = None
        while not process_id or process_id == 1:
            random_number = random.randint(0, len(processes_list)-1)
            process_id = processes_list[random_number]['pid']

        self.lg.info('Send delete  nodes/{nodeid}/containers/containerid/processes/processid api request.')
        response = self.containers_api.delete_containers_containerid_processes_processid(self.node_id, container_name,
                                                                                         str(process_id))
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that deletd process deleted from process list.')
        response = self.containers_api.get_containers_containerid_processes(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        for process in processes_list:
            self.assertNotEqual(process['pid'], process_id)

        self.lg.info(' Compare results with golden value.')
        container=self.g8core.client.container.find(container_name)
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.g8core.client.container.client(container_id)
        golden_value = container.process.list()
        for process in golden_value:
            self.assertNotEqual(process['pid'], process_id)

    def test017_post_signal_to_process_in_container(self):
        """ GAT-038
        *get:/node/{nodeid}/containers/containerid/processes/processid Expected: get container details *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random conatainer of list of running containers.
        #. Choose one random process of list of running processes in  container.
        #. Send post nodes/{nodeid}/containers/containerid/processes/process  api request, should succeed

        """
        signal = random.randint(1, 30)
        body = {'signal': signal}
        self.lg.info('Choose one random container of list of running nodes')
        container_name = self.get_random_container(self.node_id)
        self.assertTrue(container_name)
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, container_name,
                                                                        self.job_body)

        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.g8core.wait_on_container_job_update(container_name, job_id, 100, False))

        self.lg.info('Choose one random process of list of processes')
        response = self.containers_api.get_containers_containerid_processes(self.node_id, container_name)
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        process_id = None
        while not process_id or process_id == 1:
            random_number = random.randint(0, len(processes_list)-1)
            process_id = processes_list[random_number]['pid']

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/processes/processid api request.')
        response = self.containers_api.post_containers_containerid_processes_processid(self.node_id, container_name,
                                                                                       str(process_id), body)
        self.assertEqual(response.status_code, 204)

    @unittest.skip('https://github.com/Jumpscale/go-raml/issues/297')
    def test018_upload_file_to_container(self):
        """ GAT-039
        *post:/node/{nodeid}/containers/containerid/filesystem  *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Create new container .
        #. post /node/{nodeid}/containers/containerid/filesystem api request should succeed.
        #. Check that file exist in container .
        #. Delete  file from g8os node.
        #. Delete  file from container.
        #. Check that file doesn\'t exist in container.

        """
        self.lg.info('create container ')
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertEqual(response.status_code, 201)
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})

        self.lg.info('create file in g8os node ')
        file_name = self.rand_str()
        self.g8core.client.bash('touch %s.text'%file_name)
        body = {"file": '/%s.text'%file_name}
        params = {"path": "/%s.text"%file_name}
        response = self.containers_api.post_containers_containerid_filesystem(nodeid=self.node_id,
                                                                            containername=self.container_name,
                                                                            data=body,
                                                                            params=params)
        self.assertEqual(response.status_code,204)

        self.lg.info('Check that file exist in container ')
        container=self.g8core.client.container.find(self.container_name)
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.g8core.client.container.client(container_id)
        output = container.bash('ls | grep %s.text'%file_name).get().state
        self.assertEqual(output, "SUCCESS")

        self.lg.info('delete  file from g8os node ')
        self.g8core.client.bash('rm %s.text'%file_name)

        self.lg.info('delete  file from container ')
        body = {"path": "/%s.text"%file_name}
        response = self.containers_api.delete_containers_containerid_filesystem(nodeid=self.node_id,
                                                                              containername=self.container_name,
                                                                              data=body)
        self.assertEqual(response.status_code,204)

        self.lg.info('Check that file doesn\'t exist in container ')
        container=self.g8core.client.container.find(self.container_name)
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.g8core.client.container.client(container_id)
        output = container.bash('ls | grep %s.text'%file_name).get().state
        self.assertNotEqual(output, "SUCCESS")

    def test019_download_file_from_container(self):
        """ GAT-040
        *get:/node/{nodeid}/containers/containerid/filesystem  *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Create new container .
        #.  Make new file in container .
        #. Get /node/{nodeid}/containers/containerid/filesystem api request should succeed.
        #. Check that file downloaded
        #. Delete  file from container,

        """
        file_name = self.rand_str()
        self.lg.info('create container ')
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertEqual(response.status_code, 201)
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})

        self.lg.info('create new file in container ')
        container=self.g8core.client.container.find(self.container_name)
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.g8core.client.container.client(container_id)
        output = container.bash('echo "test" >%s.text'%file_name).get().state
        self.assertEqual(output, "SUCCESS")

        self.lg.info('Get created file from container ')
        params = {"path": "/%s.text"%file_name}
        response = self.containers_api.get_containers_containerid_filesystem(nodeid=self.node_id,
                                                                            containername=self.container_name,
                                                                            params=params)
        self.assertTrue(response.status_code, 201)

        self.lg.info('Check that file downloaded')
        self.assertTrue(response.text, "test")

        self.lg.info('delete  file from container ')
        output = container.bash('rm %s.text'%file_name).get().state
        self.assertEqual(output, "SUCCESS")
