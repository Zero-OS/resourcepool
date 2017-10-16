import random, time, unittest
from testcases.testcases_base import TestcasesBase


class TestcontaineridAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.job_body = {'name': 'yes'}
        self.lg.info(' [*] Create new container. ')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")

    def tearDown(self):
        self.lg.info(' [*] TearDown: Delete all created container ')
        self.containers_api.delete_containers_containerid(self.nodeid, self.data['name'])

    def test001_list_containers(self):
        """ GAT-022
        *GET:/node/{nodeid}/containers Expected: List of all running containers *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Send get nodes/{nodeid}/containers api request.
        #. Compare results with core0 containers list.
        """
        self.lg.info('Send get nodes/{nodeid}/containers api request.')
        response = self.containers_api.get_containers(self.nodeid)
        self.assertEqual(response.status_code, 200)
        data = {
            "flist": self.data['flist'],
            "hostname": self.data['hostname'],
            "name": self.data['name'],
            "status": "running"
        }
        self.assertIn(data, response.json())

    def test002_create_containers(self):
        """ GAT-023
        *post:/node/{nodeid}/containers Expected: create container then delete it *

        **Test Scenario:**

        #. Create new container (setup method)
        #. Delete created container,should succeed.
        #. Create container with same name of C1, should fail
        #. make sure that it deleted .
        """
        self.lg.info('Make sure it created with required values, should succeed.')
        self.assertEqual(self.response.headers['Location'], "/nodes/{}/containers/{}".format(self.nodeid, self.data['name']))

        response = self.containers_api.get_containers_containerid(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        for key in response_data.keys():
            if key == 'initprocesses':
                self.assertEqual(response_data[key], self.data['initProcesses'])
                continue

            if key in self.data.keys():
                self.assertEqual(response_data[key], self.data[key])

        self.lg.info('Create container with same name of C1, should fail')
        response, data = self.containers_api.post_containers(nodeid=self.nodeid, name=self.data['name'])
        self.assertEqual(response.status_code, 409)

        self.lg.info('delete created container')
        response = self.containers_api.delete_containers_containerid(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('Make sure that it deleted ')
        response = self.containers_api.get_containers(self.nodeid)
        self.assertNotIn(self.data['name'], [container['name'] for container in response.json()])
        self.assertFalse(self.core0_client.client.container.find(self.data['name']), 'container {} still exist in node'.format(self.data['name']))


    def test003_get_container_details(self):
        """ GAT-024
        *get:/node/{nodeid}/containers/containerid Expected: get container details *

        **Test Scenario:**

        #. Get:/node/{nodeid}/containers/containerid
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Send get nodes/{nodeid}/containers/containerid api request.')
        response = self.containers_api.get_containers_containerid(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.lg.info(' [*] Compare results with golden value.')
        golden_value = self.core0_client.get_container_info(self.data['name'])
        self.assertTrue(golden_value)
        for key in data.keys():
            if key in golden_value.keys():
                self.assertEqual(data[key], golden_value[key])

    def test004_stop_and_start_container(self):
        """ GAT-025
        *post:/node/{nodeid}/containers/containerid/start Expected: get container details *

        **Test Scenario:**

        #. post:/node/{nodeid}/containers/containerid/stop.
        #. Check that container stpoed .
        #. Post:/node/{nodeid}/containers/containerid/start.
        #. Check that container running .

        """
        self.lg.info('post:/node/{nodeid}/containers/containerid/stop.')
        response = self.containers_api.post_containers_containerid_stop(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that container stoped.')
        self.assertTrue(self.core0_client.wait_on_container_update(self.data['name'], 60, True))

        self.lg.info('post:/node/{nodeid}/containers/containerid/start.')
        response = self.containers_api.post_containers_containerid_start(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 201)

        self.lg.info('Check that container running.')
        self.assertTrue(self.core0_client.wait_on_container_update(self.data['name'], 60, False))

    def test005_get_running_jobs(self):
        """ GAT-026
        *get:/node/{nodeid}/containers/containerid/jobs Expected: get container details *

        **Test Scenario:**

        #. Get:/node/{nodeid}/containers/containerid/jobs
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Send get nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.get_containers_containerid_jobs(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)

        self.lg.info('Compare results with golden value.')
        running_jobs_list = response.json()
        golden_values = self.core0_client.get_container_job_list(self.data['name'])

        api_jobs = set([(job['id'], job['startTime']) for job in running_jobs_list])
        self.assertEqual(len(golden_values.difference(api_jobs)), 1)

    def test006_post_new_job_in_container(self):
        """ GAT-027
        *post:/node/{nodeid}/containers/containerid/jobs *

        **Test Scenario:**

        #. Send post nodes/{nodeid}/containers/containerid/jobs request.
        #. Check that you can get created job.

        """
        self.lg.info(' [*] Send post  nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'], job_id, 100, False))

        self.lg.info(' [*] Check that you can get created job.')
        time.sleep(7)
        response = self.containers_api.get_containers_containerid_jobs_jobid(self.nodeid, self.data['name'], job_id)
        self.assertEqual(response.status_code, 200)

    def test007_kill_all_running_jobs(self):
        """ GAT-028
        *get:/node/{nodeid}/containers/containerid/jobs Expected: get container details*

        **Test Scenario:**

        #. delete :/node/{nodeid}/containers/containerid/jobs.
        #. Check that all jobs in this container killed.

        """
        self.lg.info(' [*] Spawn multiple jobs.')
        for i in range(0, 3):
            response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                            self.job_body)
            self.assertEqual(response.status_code, 202)
            job_id = response.headers['Location'].split('/')[6]
            self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'], job_id, 15, False))

        self.lg.info(' [*] Send delete nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.delete_containers_containerid_jobs(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 204)
        time.sleep(5)

        self.lg.info(' [*] Check that all jobs in this container killed ')
        response = self.containers_api.get_containers_containerid_jobs(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        jobs_list = response.json()
        self.assertEqual(len(jobs_list), 1)
        self.assertEqual(len(self.core0_client.get_container_job_list(self.data['name'])), 1)

    def test008_get_job_in_container_details(self):
        """ GAT-029
        *get:/node/{nodeid}/containers/containerid/jobs/jobid Expected: get container details *

        **Test Scenario:**

        #. Send get nodes/{nodeid}/containers/containerid/jobs/jobid api request
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Spawn job in container ')
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'], job_id, 100, False))

        self.lg.info(' [*] Send get nodes/{nodeid}/containers/containerid/jobs/jobid api request.')
        response = self.containers_api.get_containers_containerid_jobs_jobid(self.nodeid, self.data['name'], job_id)
        self.assertEqual(response.status_code, 200)
        job_details = response.json()

        self.lg.info(' [*] Compare results with golden value.')
        container_id = int(list(self.core0_client.client.container.find(self.data['name']).keys())[0])
        container = self.core0_client.client.container.client(container_id)
        golden_value = container.job.list(job_id)[0]
        self.assertEqual(golden_value['cmd']['command'], job_details['name'])
        self.assertEqual(golden_value['cmd']['id'], job_details['id'])
        self.assertEqual(golden_value['starttime'], job_details['startTime'])

        response = self.containers_api.delete_containers_containerid_jobs_jobid(self.nodeid, self.data['name'], job_id)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'], job_id, 100, True))
        
    def test009_post_signal_job_in_container_details(self):
        """ GAT-030
        *get:/node/{nodeid}/containers/containerid/jobs/jobid Expected: get container details *

        **Test Scenario:**
        #. Choose one random job of list of running jobs in  container.
        #. Send post nodes/{nodeid}/containers/containerid/jobs/jobid api request, should succeed

        """
        signal = random.randint(1, 30)
        body = {'signal': signal}

        self.lg.info(' spawn job in container ')
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/jobs/jobid api request.')
        response = self.containers_api.post_containers_containerid_jobs_jobid(self.nodeid, self.data['name'],
                                                                              job_id, body)
        self.assertEqual(response.status_code, 204)

    def test010_kill_specific_job(self):
        """ GAT-031
        *get:/node/{nodeid}/containers/containerid/jobs/jobid Expected: get container details *

        **Test Scenario:**

        #. Choose one random job of list of running jobs in  container.
        #. Send delete nodes/{nodeid}/containers/containerid/jobs/jobid api request, should succeed
        #. Check that job delted from running jobs list.
        #. Check that job delted from client list.
        """
        self.lg.info(' [*] Spawn job in container ')
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'],
                                                                       job_id, 60, False))

        self.lg.info(' [*] Send delete  nodes/{nodeid}/containers/containerid/jobs/jobid api request.')
        response = self.containers_api.delete_containers_containerid_jobs_jobid(self.nodeid, self.data['name'], job_id)
        self.assertEqual(response.status_code, 204)

        time.sleep(3)
        
        self.lg.info(' [*] Check that job deleted from running jobs list.')
        response = self.containers_api.get_containers_containerid_jobs(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        running_jobs_list = response.json()
        self.assertNotIn(job_id, running_jobs_list)

        self.lg.info('Check that job delted from client list.')
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'],
                                                                       job_id, 60, True))

    def test011_post_ping_to_container(self):
        """ GAT-032
        *get:/node/{nodeid}/containers/containerid/ping *

        **Test Scenario:**

        #. Send post nodes/{nodeid}/containers/containerid/post request.

        """
        self.lg.info(' [*] Send post  nodes/{nodeid}/containers/containerid/ping api request.')
        response = self.containers_api.post_containers_containerid_ping(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)

    def test012_get_state_of_container(self):
        """ GAT-033
        *get:/node/{nodeid}/containers/containerid/state *

        **Test Scenario:**

        #. Send get nodes/{nodeid}/containers/containerid/state request.
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Send GET  nodes/{nodeid}/containers/containerid/state api request.')
        response = self.containers_api.get_containers_containerid_state(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)

        self.lg.info(' [*] Compare results with golden value.')
        container_state = response.json()
        container_id = int(list(self.core0_client.client.container.find(self.data['name']).keys())[0])
        golden_value = self.core0_client.client.container.list()[str(container_id)]
        self.assertEqual(golden_value['swap'], container_state['swap'])

    def test013_get_info_of_container_os(self):
        """ GAT-034
        *get:/node/{nodeid}/containers/containerid/info *

        **Test Scenario:**

        #. Send get nodes/{nodeid}/containers/containerid/info request.
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Send post  nodes/{nodeid}/containers/containerid/state api request.')
        response = self.containers_api.get_containers_containerid_info(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)

        self.lg.info(' [*] Compare results with golden value.')
        container_info = response.json()
        container_id = int(list(self.core0_client.client.container.find(self.data['name']).keys())[0])
        container = self.core0_client.client.container.client(container_id)
        golden_value = container.info.os()
        self.assertAlmostEqual(golden_value.pop('uptime'), container_info.pop('uptime'), delta=50)
        for key in container_info:
            if key not in golden_value:
                self.assertEqual(golden_value[key], container_info[key])

    def test014_get_running_processes_in_container(self):
        """ GAT-035
        *get:/node/{nodeid}/containers/containerid/processes *

        **Test Scenario:**

        #. Send get nodes/{nodeid}/containers/containerid/processes request.
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Send post  nodes/{nodeid}/containers/containerid/state api request.')
        response = self.containers_api.get_containers_containerid_processes(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        processes = response.json()
        container_id = int(list(self.core0_client.client.container.find(self.data['name']).keys())[0])
        container = self.core0_client.client.container.client(container_id)
        golden_values = container.process.list()

        self.lg.info(' [*] Compare results with golden value.')
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

        #. Choose one random process of list of process.
        #. Send get nodes/{nodeid}/containers/containerid/processes/processid request.
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Choose one random process of list of process.')
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                        self.job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'], job_id, 100, False))

        response = self.containers_api.get_containers_containerid_processes(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        process_id = None
        while not process_id or process_id == 1:
            random_number = random.randint(0, len(processes_list) - 1)
            process_id = processes_list[random_number]['pid']

        self.lg.info(' [*] Send get  nodes/{nodeid}/containers/containerid/processes/processid api request.')
        response = self.containers_api.get_containers_containerid_processes_processid(self.nodeid, self.data['name'],
                                                                                      str(process_id))
        self.assertEqual(response.status_code, 200)
        process = response.json()
        container_id = int(list(self.core0_client.client.container.find(self.data['name']).keys())[0])
        container = self.core0_client.client.container.client(container_id)
        golden_value = container.process.list(process_id)[0]

        self.lg.info(' [*] Compare results with golden value.')
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

        #. Choose one random process of list of process.
        #. Send delete nodes/{nodeid}/containers/containerid/processes/processid request.
        #. Check that created process deleted from process list.
        #. Compare results with golden value.

        """
        self.lg.info(' [*] Choose one random process of list of processes')
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                        self.job_body)

        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'], job_id, 100, False))
        response = self.containers_api.get_containers_containerid_processes(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        process_id = None
        while not process_id or process_id == 1:
            random_number = random.randint(0, len(processes_list) - 1)
            process_id = processes_list[random_number]['pid']

        self.lg.info(' [*] Send delete  nodes/{nodeid}/containers/containerid/processes/processid api request.')
        response = self.containers_api.delete_containers_containerid_processes_processid(self.nodeid, self.data['name'],
                                                                                         str(process_id))
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that deletd process deleted from process list.')
        response = self.containers_api.get_containers_containerid_processes(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        for process in processes_list:
            self.assertNotEqual(process['pid'], process_id)

        self.lg.info(' Compare results with golden value.')
        container = self.core0_client.client.container.find(self.data['name'])
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.core0_client.client.container.client(container_id)
        golden_value = container.process.list()
        for process in golden_value:
            self.assertNotEqual(process['pid'], process_id)


    def test017_post_signal_to_process_in_container(self):
        """ GAT-038
        *get:/node/{nodeid}/containers/containerid/processes/processid Expected: get container details *

        **Test Scenario:**

        #. Choose one random process of list of running processes in  container.
        #. Send post nodes/{nodeid}/containers/containerid/processes/process  api request, should succeed

        """
        signal = random.randint(1, 30)
        body = {'signal': signal}
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, self.data['name'],
                                                                        self.job_body)

        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.core0_client.wait_on_container_job_update(self.data['name'], job_id, 100, False))

        self.lg.info('Choose one random process of list of processes')
        response = self.containers_api.get_containers_containerid_processes(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        processes_list = response.json()
        process_id = None
        while not process_id or process_id == 1:
            random_number = random.randint(0, len(processes_list) - 1)
            process_id = processes_list[random_number]['pid']

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/processes/processid api request.')
        response = self.containers_api.post_containers_containerid_processes_processid(self.nodeid, self.data['name'],
                                                                                       str(process_id), body)
        self.assertEqual(response.status_code, 204)

    def test018_upload_file_to_container(self):
        """ GAT-039
        *post:/node/{nodeid}/containers/containerid/filesystem  *

        **Test Scenario:**

        #. post /node/{nodeid}/containers/containerid/filesystem api request should succeed.
        #. Check that file exist in container .
        #. Delete  file from g8os node.
        #. Delete  file from container.
        #. Check that file doesn\'t exist in container.

        """
        self.lg.info(' [*] create file in g8os node ')
        file_name = self.rand_str()
        self.core0_client.client.bash('touch %s.text' % file_name)
        body = {"file": '/%s.text' % file_name}
        params = {"path": "/%s.text" % file_name}
        response = self.containers_api.post_containers_containerid_filesystem(nodeid=self.nodeid,
                                                                              containername=self.data['name'],
                                                                              data=body,
                                                                              params=params)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that file exist in container ')
        container = self.core0_client.client.container.find(self.data['name'])
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.core0_client.client.container.client(container_id)
        output = container.bash('ls | grep %s.text' % file_name).get().state
        self.assertEqual(output, "SUCCESS")

        self.lg.info('delete  file from g8os node ')
        self.core0_client.client.bash('rm %s.text' % file_name)

        self.lg.info('delete  file from container ')
        body = {"path": "/%s.text" % file_name}
        response = self.containers_api.delete_containers_containerid_filesystem(nodeid=self.nodeid,
                                                                                containername=self.data['name'],
                                                                                data=body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that file doesn\'t exist in container ')
        container = self.core0_client.client.container.find(self.data['name'])
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.core0_client.client.container.client(container_id)
        output = container.bash('ls | grep %s.text' % file_name).get().state
        self.assertNotEqual(output, "SUCCESS")

    def test019_download_file_from_container(self):
        """ GAT-040
        *get:/node/{nodeid}/containers/containerid/filesystem  *

        **Test Scenario:**

        #.  Make new file in container .
        #. Get /node/{nodeid}/containers/containerid/filesystem api request should succeed.
        #. Check that file downloaded
        #. Delete  file from container,

        """
        file_name = self.rand_str()
        self.lg.info(' [*] Create container ')

        self.lg.info(' [*] Create new file in container ')
        container = self.core0_client.client.container.find(self.data['name'])
        self.assertTrue(container)
        container_id = int(list(container.keys())[0])
        container = self.core0_client.client.container.client(container_id)
        output = container.bash('echo "test" >%s.text' % file_name).get().state
        self.assertEqual(output, "SUCCESS")

        self.lg.info(' [*] Get created file from container ')
        params = {"path": "/%s.text" % file_name}
        response = self.containers_api.get_containers_containerid_filesystem(nodeid=self.nodeid,
                                                                             containername=self.data['name'],
                                                                             params=params)
        self.assertTrue(response.status_code, 201)

        self.lg.info('Check that file downloaded')
        self.assertTrue(response.text, "test")

        self.lg.info('delete  file from container ')
        output = container.bash('rm %s.text' % file_name).get().state
        self.assertEqual(output, "SUCCESS")

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1212')
    def test020_get_container_nics(self):
        """ GAT-148
        *get:/node/{nodeid}/containers/containerid/nics  *

        **Test Scenario:**

        #. Get random node (N0).
        #. Create bridge (B0) on node (N0).
        #. Create container (C0) on node (N0) and attach bridge (B0) to it.
        #. Get container (C0) nic info, should succeed.
        #. Get container (C0) nic info using core0 client.
        #. Compare results, should succeed.
        #. Update container (C0) nics, should succeed.
        #. Get container (C0) nic info, should succeed.
        #. Compare results, should succeed.
        #. Delete contaienr (C0), should succeed.
        #. Delete bridge (B0), should succeed.

        """
        
        self.lg.info(' [*] Create bridge (B0) on node (N0)')
        response, bridge_data = self.bridges_api.post_nodes_bridges(node_id=self.nodeid, networkMode='dnsmasq')
        self.assertEqual(response.status_code, 201)

        self.lg.info(' [*] Create container (C0) on node (N0) and attach bridge (B0) to it')
        nics = [{"type":"default"}, {"id":bridge_data['name'], "type":"bridge", "name":"test", "status":"up"}]
        response, container_data = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics)
        self.assertEqual(response.status_code, 201)

        self.lg.info(' [*] Get container (C0) nic info, should succeed')
        response = self.containers_api.get_container_nics(nodeid=self.nodeid, containername=container_data['name'])
        self.assertEqual(response.status_code, 200)
        orchestrator_nic_info = response.json()
        
        self.lg.info(' [*] Get container (C0) nic info using core0 client')
        container_client = self.core0_client.get_container_client(container_data['name'])
        core0_nic_info = container_client.info.nic()
        
        self.lg.info(' [*] Compare results, should succeed')
        self.assertEqual(len(core0_nic_info), len(orchestrator_nic_info))
        for i in range(len(orchestrator_nic_info)):
            if not orchestrator_nic_info[i]['addrs']:
                orchestrator_nic_info[i]['addrs'] = []

            core0_nic_info[i]['addrs'] = [x['addr'] for x in core0_nic_info[i]['addrs']]
            del core0_nic_info[i]['speed']

            self.assertDictEqual(orchestrator_nic_info[i], core0_nic_info[i])

        self.lg.info(' [*] Update container (C0) nics, should succeed')
        nics = [{"type":"default"}]
        response, data = self.containers_api.update_container(nodeid=self.nodeid, containername=container_data['name'], nics=nics)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Get container (C0) nic info, should succeed')
        response = self.containers_api.get_container_nics(nodeid=self.nodeid, containername=container_data['name'])
        self.assertEqual(response.status_code, 200)
        orchestrator_nic_info = response.json()

        self.lg.info(' [*] Compare results, should succeed')
        self.assertEqual(len(data['nics']), len([x for x in orchestrator_nic_info if 'eth' in x['name']]))

        self.lg.info(' [*] Delete contaienr (C0), should succeed')
        response = self.containers_api.delete_containers_containerid(nodeid=self.nodeid, containername=container_data['name'])
        self.assertEqual(response.status_code, 204)
        
        self.lg.info(' [*] Delete bridge (B0), should succeed')
        response = self.bridges_api.delete_nodes_bridges_bridgeid(nodeid=self.nodeid, bridgeid=bridge_data['name'])
        self.assertEqual(response.status_code, 204)

    def test022_get_container_memory(self):
        """ GAT-149
        *get:/node/{nodeid}/containers/containerid/mem  *

        **Test Scenario:**

        #. Get random node (N0).
        #. Create container (C0) on node (N0), should succeed.
        #. Get container (C0) memory info, should succeed.
        #. Get container (C0) memory info using core0 client.
        #. Compare results, should succeed.

        """
        self.lg.info(' [*] Get container (C0) memory info, should succeed')
        response = self.containers_api.get_container_mem(nodeid=self.nodeid, containername=self.data['name'])
        self.assertEqual(response.status_code, 200)
        orchestrator_mem_info = response.json()

        self.lg.info(' [*] Get container (C0) memory info using core0 client')
        container_client = self.core0_client.get_container_client(self.data['name'])
        core0_mem_info = container_client.info.mem()

        for key in orchestrator_mem_info.keys():
            delta = 0.1 * orchestrator_mem_info[key]
            self.assertAlmostEquals(core0_mem_info[key], orchestrator_mem_info[key], delta=delta)
    
    def test023_get_container_cpus(self):
        """ GAT-150
        *get:/node/{nodeid}/containers/containerid/cpus  *

        **Test Scenario:**

        #. Get random node (N0).
        #. Create container (C0) on node (N0), should succeed.
        #. Get container (C0) cpus info, should succeed.
        #. Get container (C0) cpus info using core0 client.
        #. Compare results, should succeed.

        """
        self.lg.info(' [*] Get container (C0) cpus info, should succeed')
        response = self.containers_api.get_container_cpus(nodeid=self.nodeid, containername=self.data['name'])
        self.assertEqual(response.status_code, 200)
        orchestrator_cpu_info = response.json()

        self.lg.info(' [*] Get container (C0) cpus info using core0 client')
        container_client = self.core0_client.get_container_client(self.data['name'])
        core0_cpu_info = container_client.info.cpu()
        
        for i in range(len(orchestrator_cpu_info)):
            for key in orchestrator_cpu_info[i].keys():
                self.assertEqual(orchestrator_cpu_info[i][key], core0_cpu_info[i][key])



            




