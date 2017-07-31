import random, time
from testcases.testcases_base import TestcasesBase
import unittest


class TestVmsAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        storageclusters = self.storageclusters_api.get_storageclusters()
        if storageclusters.json() == []:
            self.lg.info(' [*] Create new storagecluster.')
            response, body = self.storageclusters_api.post_storageclusters(node_id=self.nodeid)
            self.assertEqual(response.status_code, 201)
            self.storagecluster = body['label']
        else:
            self.storagecluster = storageclusters.json()[0]

        vdisks = self.vdisks_api.get_vdisks()
        vdisks = [x for x in vdisks.json() if
                  (x['id'] == 'ubuntu-test-vdisk' and x['storageCluster'] == self.storagecluster)]
        if vdisks == []:
            self.lg.info(' [*] Create new ssd vdisk.')
            response, self.vdisk = self.vdisks_api.post_vdisks(id='ubuntu-test-vdisk', size=15,
                                                               blocksize=4096, type='boot',
                                                               storagecluster=self.storagecluster,
                                                               templatevdisk="ardb://hub.gig.tech:16379/template:ubuntu-1604")
            self.assertEqual(response, 201, " [*] Can't create vdisk.")
        else:
            self.vdisk = vdisks[0]

        self.lg.info(' [*] Create virtual machine (VM0) on node (N0)')
        self.response, self.data = self.vms_api.post_nodes_vms(node_id=self.nodeid, memory=1024, cpu=1)
        self.assertEqual(self.response.status_code, 201)

    def tearDown(self):
        self.lg.info(' [*] Delete virtual machine (VM0)')
        self.vms_api.delete_nodes_vms_vmid(self.nodeid, self.data['id'])
        super(TestVmsAPI, self).tearDown()

    def test001_get_nodes_vms_vmid(self):
        """ GAT-067
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Get virtual machine (VM0), should succeed with 200.
        #. Get non existing virtual machine, should fail with 404.
        """
        self.lg.info(' [*] Get virtual machine (VM0), should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 200)
        keys_to_check = ['id', 'memory', 'cpu', 'nics', 'disks']
        for key in keys_to_check:
            self.assertEqual(self.data[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'running')

        vms_list = self.core0_client.client.kvm.list()
        self.assertIn(self.data['id'], [x['name'] for x in vms_list])

        self.lg.info(' [*] Get non existing virtual machine, should fail with 404')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, 'fake_vm')
        self.assertEqual(response.status_code, 404)

    def test002_get_node_vms(self):
        """ GAT-068
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. List node (N0) virtual machines, virtual machine (VM0) should be listed, should succeed with 200.
        """
        self.lg.info(
            ' [*] List node (N0) virtual machines, virtual machine (VM0) should be listed, should succeed with 200')
        response = self.vms_api.get_nodes_vms(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['id'], [x['id'] for x in response.json()])

    def test003_post_node_vms(self):
        """ GAT-069
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM1) on node (N0).
        #. Get virtual machine (VM1), should succeed with 200.
        #. List kvms in python client, (VM1) should be listed.
        #. Delete virtual machine (VM1), should succeed with 204.
        #. Create virtual machine with missing parameters, should fail with 400.
        """
        self.lg.info(' [*] Create virtual machine (VM0) on node (N0)')
        response_vm, data_vm = self.vms_api.post_nodes_vms(node_id=self.nodeid)
        self.assertEqual(response_vm.status_code, 201, " [*] Can't create new vm.")

        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, data_vm['id'])
        self.assertEqual(response.status_code, 200, " [*] Can't create new vm.")

        if response.json()['status'] == 'error':
            response_vm, data_vm = self.vms_api.post_nodes_vms(node_id=self.nodeid, memory=1024, cpu=1)
            self.assertEqual(response_vm.status_code, 201)

        self.lg.info(' [*] Get virtual machine (VM1), should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, data_vm['id'])
        self.assertEqual(response.status_code, 200)
        keys_to_check = ['id', 'memory', 'cpu', 'nics', 'disks']
        for key in keys_to_check:
            self.assertEqual(data_vm[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'running')

        self.lg.info(' [*] List kvms in python client, (VM1) should be listed')
        vms = self.core0_client.client.kvm.list()
        self.assertIn(data_vm['id'], [x['name'] for x in vms])

        self.lg.info(' [*] Delete virtual machine (VM1), should succeed with 204')
        response = self.vms_api.delete_nodes_vms_vmid(self.nodeid, data_vm['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Create virtual machine with missing parameters, should fail with 400')
        response, data = self.vms_api.post_nodes_vms(self.nodeid, memory='')
        self.assertEqual(response.status_code, 400)

    def test004_put_nodes_vms_vmid(self):
        """ GAT-070
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Update virtual machine (VM1), should succeed with 201.
        #. Get virtual machine (VM1), should succeed with 200.
        #. Update virtual machine with missing parameters, should fail with 400.
        """
        vm_mem = 2 * 1024
        vm_cpu = 2
        vm_nics = []
        vm_disks = [{
            "vdiskid": "ubuntu-test-vdisk",
            "maxIOps": 2000
        }]
        body = {"memory": vm_mem,
                "cpu": vm_cpu,
                "nics": vm_nics,
                "disks": vm_disks}

        self.lg.info(' [*] Stop virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_stop(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Get virtual machine (VM0), virtual machine (VM0) status should be halting')
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'halted':
                break
            else:
                time.sleep(3)
        else:
            self.lg.error(" [*] Can't stop the vm.")
            self.assertEqual(response.json()['status'], 'halted', " [*] Can't stop the vm.")

        response = self.vms_api.put_nodes_vms_vmid(self.nodeid, self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Start virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_start(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'running':
                break
            else:
                time.sleep(3)
        else:
            self.lg.error(" [*] can't start vm.")
            self.assertEqual(response.json()['status'], 'running', " [*] can't start vm.")

        self.lg.info(' [*] Get virtual machine (VM0), should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 200)

        keys_to_check = ['memory', 'cpu', 'nics', 'disks']
        for key in keys_to_check:
            self.assertEqual(body[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'running')

        self.lg.info(' [*] Update virtual machine with missing parameters, should fail with 400')
        body = {"id": self.random_string()}
        response = self.vms_api.put_nodes_vms_vmid(self.nodeid, self.data['id'], body)
        self.assertEqual(response.status_code, 400)

    def test005_get_nodes_vms_vmid_info(self):
        """ GAT-071
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Get virtual machine (VM0) info, should succeed with 200.
        #. Get non existing virtual machine info, should fail with 404.
        """
        self.lg.info(' [*] Get virtual machine (VM0) info, should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid_info(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 200)

        self.lg.info(' [*] Get non existing virtual machine info, should fail with 404')
        response = self.vms_api.get_nodes_vms_vmid_info(self.nodeid, self.rand_str())
        self.assertEqual(response.status_code, 404, " [*] get non existing vm returns %i" % response.status_code)

    def test006_delete_nodes_vms_vmid(self):
        """ GAT-072
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Delete virtual machine (VM0), should succeed with 204.
        #. List kvms in python client, (VM0) should be gone.
        #. Delete non existing virtual machine, should fail with 404.
        """
        self.lg.info(' [*] Delete virtual machine (VM0), should succeed with 204')
        response = self.vms_api.delete_nodes_vms_vmid(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List kvms in python client, (VM0) should be gone')
        vms = self.core0_client.client.kvm.list()
        self.assertNotIn(self.data['id'], [x['name'] for x in vms])

        self.lg.info(' [*] Delete non existing virtual machine, should fail with 404')
        response = self.vms_api.delete_nodes_vms_vmid(self.nodeid, self.rand_str(),
                                                      " [*] Delete non existing virtual machine should return 404 ")
        self.assertEqual(response.status_code, 404)

    def test007_post_nodes_vms_vmid_start(self):
        """ GAT-073
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Stop virtual machine (VM0), should succeed with 204.
        #. Start virtual machine (VM0), should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be running.
        """
        self.lg.info(' [*] Stop virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_stop(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'halted':
                break
            else:
                time.sleep(3)
        else:
            self.assertEqual(response.json()['status'], 'halted', " [*] can't stop vm.")

        vms = self.core0_client.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == self.data['id']]
        self.assertEqual(vm0, [])

        self.lg.info(' [*] Start virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_start(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'running':
                break
            else:
                time.sleep(3)
        else:
            self.assertEqual(response.json()['status'], 'running', " [*] can't start vm.")

        vms = self.core0_client.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == self.data['id']]
        self.assertNotEqual(vm0, [])
        self.assertEquals(vm0[0]['state'], 'running')

    def test009_post_nodes_vms_vmid_pause_resume(self):
        """ GAT-075
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Pause virtual machine (VM0), should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be paused.
        #. Resume virtual machine (VM0), should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be running
        """
        self.lg.info(' [*] Pause virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_pause(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Get virtual machine (VM0), virtual machine (VM0) status should be halting')
        for _ in range(15):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'paused':
                break
            else:
                time.sleep(1)
        else:
            self.assertEqual(response.json()['status'], 'paused', " [*] can't pause the vm.")

        vms = self.core0_client.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == self.data['id']]
        self.assertNotEqual(vm0, [])
        self.assertEquals(vm0[0]['state'], 'paused')

        self.lg.info(' [*] Resume virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_resume(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Get virtual machine (VM0), virtual machine (VM0) status should be running')
        for _ in range(15):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'running':
                break
            else:
                time.sleep(1)
        else:
            self.assertEqual(response.json()['status'], 'running', " [*] can't run the vm.")

        vms = self.core0_client.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == self.data['id']]
        self.assertNotEqual(vm0, [])
        self.assertEquals(vm0[0]['state'], 'running')

    @unittest.skip('https://github.com/g8os/resourcepool/issues/128')
    def test010_post_nodes_vms_vmid_shutdown(self):
        """ GAT-076
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Shutdown virtual machine (VM0), should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be halted.
        """
        self.lg.info(' [*] Shutdown virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_shutdown(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(15):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status in ['halting', 'halted']:
                break
            else:
                time.sleep(1)
        else:
            raise AssertionError('{} not {}'.format(status, 'halting or halted'))

        vms = self.core0_client.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == self.data['id']]
        self.assertEqual(vm0, [])

    @unittest.skip('https://github.com/g8os/resourcepool/issues/215')
    def test011_post_nodes_vms_vmid_migrate(self):
        """ GAT-077
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Migrate virtual machine (VM0) to another node, should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be migrating.
        """
        self.lg.info(' [*] List nodes.')
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        nodes_list = [x['id'] for x in response.json() if x['status'] == 'running']

        if len(nodes_list) < 2:
            self.skipTest('need at least 2 nodes')

        self.lg.info(' [*] Migrate virtual machine (VM0) to another node, should succeed with 204')
        node_2 = self.get_random_node(except_node=self.nodeid)
        body = {"nodeid": node_2}
        response = self.vms_api.post_nodes_vms_vmid_migrate(self.nodeid, self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        time.sleep(30)

        response = self.vms_api.get_nodes_vms_vmid(node_2, self.data['id'])
        self.assertEqual(response.status_code, 200)

        core0_client_ip = [x['ip'] for x in nodes_list if x['id'] == node_2]
        self.assertNotEqual(core0_client_ip, [])
        vms = self.core0_client.client.kvm.list()
        self.assertIn(self.data['id'], [x['name'] for x in vms])
