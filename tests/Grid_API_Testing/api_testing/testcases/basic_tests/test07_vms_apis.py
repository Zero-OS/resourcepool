import random
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.grid_apis.orchestrator_client.vms_apis import VmsAPI
from api_testing.grid_apis.orchestrator_client.storageclusters_apis import Storageclusters
from api_testing.grid_apis.orchestrator_client.vdisks_apis import VDisksAPIs
from api_testing.utiles.core0_client import Client
import time, unittest

@unittest.skip('https://github.com/g8os/resourcepool/issues/298')
class TestVmsAPI(TestcasesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vms_api = VmsAPI()
        self.storageclusters_api = Storageclusters()
        self.vdisks_apis = VDisksAPIs()

    def setUp(self):
        super(TestVmsAPI, self).setUp()
        self.lg.info('Get random nodid (N0)')
        self.nodeid = self.get_random_node()
        nodeip = [x['ip'] for x in self.nodes if x['id'] == self.nodeid][0]
        self.pyclient = Client(nodeip, password=self.jwt)

        storageclusters = self.storageclusters_api.get_storageclusters()
        if storageclusters.json() == []:
            self.storagecluster = self.create_sotragecluster()['label']
        else:
            self.storagecluster = storageclusters.json()[0]

        vdisks = self.vdisks_apis.get_vdisks()
        vdisks = [x for x in vdisks.json() if (x['id'] == 'ubuntu-test-vdisk' and x['storageCluster'] == self.storagecluster)]
        if vdisks == []:
            self.vdisk = self.create_boot_vdisk(self.storagecluster)
        else:
            self.vdisk = vdisks[0]


    def tearDown(self):
        self.lg.info('Delete virtual machine (VM0)')
        response = self.vms_api.get_nodes_vms(self.nodeid)
        if response.status_code == 200:
            vms = response.json()
            for vm in vms:
                self.vms_api.delete_nodes_vms_vmid(self.nodeid, vm['id'])

        super(TestVmsAPI, self).tearDown()

    
    
    def create_sotragecluster(self):
        free_disks = self.pyclient.getFreeDisks()
        if free_disks == []:
            self.skipTest('no free disks to create storagecluster')

        self.lg.info('Deploy new storage cluster (SC0)')
        label = self.rand_str()
        servers = random.randint(1, len(free_disks))
        drivetype = 'ssd'
        nodes = [self.nodeid]
        body = {"label": label,
                "servers": servers,
                "driveType": drivetype,
                "clusterType": "storage",
                "nodes":nodes}

        self.storageclusters_api.post_storageclusters(body)

        for _ in range(60):
            response = self.storageclusters_api.get_storageclusters_label(label)
            if response.status_code == 200:
                if response.json()['status'] == 'ready':
                    break
                else:
                    time.sleep(3)
            else:
                time.sleep(10)
        else:
            self.lg.error('storagecluster status is not ready after 180 sec')

        return body


    def create_boot_vdisk(self, storagecluster):
        body = {"id": 'ubuntu-test-vdisk',
                "size": 15,
                "blocksize": 4096,
                "type": 'boot',
                "storagecluster": storagecluster,
                "templatevdisk":"ardb://hub.gig.tech:16379/template:ubuntu-1604"}

        self.vdisks_apis.post_vdisks(body)
        time.sleep(30)
        return body

    def create_vm(self):
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vmid = self.random_string()
        mem = 1024
        cpu = 1
        nics = []
        disks = [{
                    "vdiskid": "ubuntu-test-vdisk",
                    "maxIOps": 2000
		        }]
        userCloudInit = {}
        systemCloudInit = {}

        body = {"id":vmid,
                "memory":mem,
                "cpu":cpu,
                "nics":nics,
                "disks":disks,
                "userCloudInit":userCloudInit,
                "systemCloudInit":systemCloudInit}

        self.vms_api.post_nodes_vms(self.nodeid, body)

        for _ in range(60):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vmid)
            if response.status_code == 200:
                if response.json()['status'] == 'running':
                    break
                else:
                    time.sleep(3)
            else:
                time.sleep(10)
        else:
            self.lg.error('vm status is not running after 180 sec')
        
        return body
    
    
    def test001_get_nodes_vms_vmid(self):
        """ GAT-067
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Get virtual machine (VM0), should succeed with 200.
        #. Get nonexisting virtual machine, should fail with 404.
        """
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Get virtual machine (VM0), should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 200)
        keys_to_check = ['id', 'memory', 'cpu', 'nics', 'disks']
        for key in keys_to_check:
            self.assertEqual(vm[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'running')

        vms_list = self.pyclient.client.kvm.list()
        self.assertIn(vm['id'], [x['name'] for x in vms_list])

        self.lg.info('Get nonexisting virtual machine, should fail with 404')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, 'fake_vm')
        self.assertEqual(response.status_code, 404)

    def test002_get_node_vms(self):
        """ GAT-068
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. List node (N0) virtual machines, virtual machine (VM0) should be listed, should succeed with 200.
        """
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('List node (N0) virtual machines, virtual machine (VM0) should be listed, should succeed with 200')
        response = self.vms_api.get_nodes_vms(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(vm['id'], [x['id'] for x in response.json()])


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
        self.lg.info('Create virtual machine (VM1) on node (N0)')
        vm_id = self.random_string()
        vm_mem = random.randint(1,16)*1024
        vm_cpu = random.randint(1,16)
        vm_nics = []
        vm_disks = [
            {
                "vdiskid": "ubuntu-test-vdisk",
                "maxIOps": 2000
		    }]
        vm_userCloudInit = {}
        vm_systemCloudInit = {}

        body = {"id":vm_id,
                "memory":vm_mem,
                "cpu":vm_cpu,
                "nics":vm_nics,
                "disks":vm_disks,
                "userCloudInit":vm_userCloudInit,
                "systemCloudInit":vm_systemCloudInit}

        response = self.vms_api.post_nodes_vms(self.nodeid, body)
        self.assertEqual(response.status_code, 201)
        time.sleep(20)

        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm_id)
        self.assertEqual(response.status_code, 200)

        if response.json()['status'] == 'error':
            vm_id = self.rand_str()
            body['id'] = vm_id
            body['memory'] = 1024
            body['cpu'] = 1
            response = self.vms_api.post_nodes_vms(self.nodeid, body)
            self.assertEqual(response.status_code, 201)

        self.lg.info('Get virtual machine (VM1), should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm_id)
        self.assertEqual(response.status_code, 200)
        keys_to_check = ['id', 'memory', 'cpu', 'nics', 'disks']
        for key in keys_to_check:
            self.assertEqual(body[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'deploying')

        for _ in range(60):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm_id)
            if response.status_code == 200:
                if response.json()['status'] == 'running':
                    break
                else:
                    time.sleep(3)
            else:
                time.sleep(10)
        else:
            raise AssertionError('{} != {}'.format(response.json()['status'], 'running'))
    

        self.lg.info('List kvms in python client, (VM1) should be listed')
        vms = self.pyclient.client.kvm.list()
        self.assertIn(vm_id, [x['name'] for x in vms])

        self.lg.info('Delete virtual machine (VM1), should succeed with 204')
        response = self.vms_api.delete_nodes_vms_vmid(self.nodeid, vm_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Create virtual machine with missing parameters, should fail with 400')
        body = {"id":self.random_string()}
        response = self.vms_api.post_nodes_vms(self.nodeid, body)
        self.assertEqual(response.status_code, 400)

    # @unittest.skip('https://github.com/g8os/resourcepool/issues/126')
    def test004_put_nodes_vms_vmid(self):
        """ GAT-070
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Update virtual machine (VM1), should succeed with 201.
        #. Get virtual machine (VM1), should succeed with 200.
        #. Update virtual machine with missing parameters, should fail with 400.
        """
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm_mem = 2*1024
        vm_cpu = 2
        vm_nics = []
        vm_disks = [{
                        "vdiskid": "ubuntu-test-vdisk",
                        "maxIOps": 2000
		            }]
        body = {"memory":vm_mem,
                "cpu":vm_cpu,
                "nics":vm_nics,
                "disks":vm_disks}

        self.lg.info('Stop virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_stop(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('Get virtual machine (VM0), virtual machine (VM0) status should be halting')
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'halted':
                break
            else:
                time.sleep(3)
        else:
            self.lg.error('can\'t stop vm')

        response = self.vms_api.put_nodes_vms_vmid(self.nodeid, vm['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Start virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_start(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'running':
                break
            else:
                time.sleep(3)
        else:
            self.lg.error('can\'t start vm')

        self.lg.info('Get virtual machine (VM0), should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 200)

        keys_to_check = ['memory', 'cpu', 'nics', 'disks']
        for key in keys_to_check:
            self.assertEqual(body[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'running')


        self.lg.info('Update virtual machine with missing parameters, should fail with 400')
        body = {"id":self.random_string()}
        response = self.vms_api.put_nodes_vms_vmid(self.nodeid, vm['id'], body)
        self.assertEqual(response.status_code, 400)


    def test005_get_nodes_vms_vmid_info(self):
        """ GAT-071
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Get virtual machine (VM0) info, should succeed with 200.
        #. Get nonexisting virtual machine info, should fail with 404.
        """
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Get virtual machine (VM0) info, should succeed with 200')
        response = self.vms_api.get_nodes_vms_vmid_info(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 200)

        self.lg.info('Get nonexisting virtual machine info, should fail with 404')
        response = self.vms_api.get_nodes_vms_vmid_info(self.nodeid, 'fake_vm')


    def test006_delete_nodes_vms_vmid(self):
        """ GAT-072
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Delete virtual machine (VM0), should succeed with 204.
        #. List kvms in python client, (VM0) should be gone.
        #. Delete nonexisting virtual machine, should fail with 404.
        """
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Delete virtual machine (VM0), should succeed with 204')
        response = self.vms_api.delete_nodes_vms_vmid(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('List kvms in python client, (VM0) should be gone')
        vms = self.pyclient.client.kvm.list()
        self.assertNotIn(vm['id'], [x['name'] for x in vms])

        self.lg.info('Delete nonexisting virtual machine, should fail with 404')
        response = self.vms_api.delete_nodes_vms_vmid(self.nodeid, 'fake_vm_id')
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
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Stop virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_stop(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'halted':
                break
            else:
                time.sleep(3)
        else:
            raise AssertionError('{} is not {}'.format(status, 'halted'))

        vms = self.pyclient.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == vm['id']]
        self.assertEqual(vm0, [])

        self.lg.info('Start virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_start(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'running':
                break
            else:
                time.sleep(3)
        else:
            raise AssertionError('{} is not {}'.format(status, 'running'))

        vms = self.pyclient.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == vm['id']]
        self.assertNotEqual(vm0, [])
        self.assertEquals(vm0[0]['state'], 'running')


    def test008_post_nodes_vms_vmid_stop(self):
        """ GAT-074
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Stop virtual machine (VM0), should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be halting.
        """
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Stop virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_stop(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('Get virtual machine (VM0), virtual machine (VM0) status should be halting')
        for _ in range(20):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'halted':
                break
            else:
                time.sleep(3)
        else:
            raise AssertionError('{} != {}'.format(status, 'halted'))

        vms = self.pyclient.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == vm['id']]
        self.assertEqual(vm0, [])



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
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Pause virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_pause(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('Get virtual machine (VM0), virtual machine (VM0) status should be halting')
        for _ in range(15):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'paused':
                break
            else:
                time.sleep(1)
        else:
            raise AssertionError('{} != {}'.format(status, 'paused'))

        vms = self.pyclient.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == vm['id']]
        self.assertNotEqual(vm0, [])
        self.assertEquals(vm0[0]['state'], 'paused')

        self.lg.info('Resume virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_resume(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('Get virtual machine (VM0), virtual machine (VM0) status should be running')
        for _ in range(15):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status == 'running':
                break
            else:
                time.sleep(1)
        else:
            raise AssertionError('{} != {}'.format(status, 'paused'))

        vms = self.pyclient.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == vm['id']]
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
        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Shutdown virtual machine (VM0), should succeed with 204')
        response = self.vms_api.post_nodes_vms_vmid_shutdown(self.nodeid, vm['id'])
        self.assertEqual(response.status_code, 204)
        for _ in range(15):
            response = self.vms_api.get_nodes_vms_vmid(self.nodeid, vm['id'])
            self.assertEqual(response.status_code, 200)
            status = response.json()['status']
            if status in ['halting', 'halted']:
                break
            else:
                time.sleep(1)
        else:
            raise AssertionError('{} not {}'.format(status, 'halting or halted'))

        vms = self.pyclient.client.kvm.list()
        vm0 = [x for x in vms if x['name'] == vm['id']]
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
        if len(self.nodes) < 2:
            self.skipTest('need at least 2 nodes')

        self.lg.info('Create virtual machine (VM0) on node (N0)')
        vm = self.create_vm()

        self.lg.info('Migrate virtual machine (VM0) to another node, should succeed with 204')
        node_2 = self.get_random_node(except_node=self.nodeid)
        body = {"nodeid": node_2}
        response = self.vms_api.post_nodes_vms_vmid_migrate(self.nodeid, vm['id'], body)
        self.assertEqual(response.status_code, 204)

        time.sleep(30)
        
        response = self.vms_api.get_nodes_vms_vmid(node_2, vm['id'])
        self.assertEqual(response.status_code, 200)

        pyclient_ip = [x['ip'] for x in self.nodes if x['id'] == node_2]
        self.assertNotEqual(pyclient_ip, [])
        pyclient = Client(pyclient_ip)
        vms = pyclient.client.kvm.list()
        self.assertIn(vm['id'], [x['name'] for x in vms])


