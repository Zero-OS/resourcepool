import random, time, unittest
from testcases.testcases_base import TestcasesBase
from testcases.core0_client import Client
from parameterized import parameterized
#from zeroos.core0.client import Client
from testcases.core0_client import Client
import ipaddress

class TestVmsAPI(TestcasesBase):
    @classmethod
    def setUpClass(cls):
        self = cls()
        super(TestVmsAPI, self).setUp()

        self.lg.info('[*] List nodes.')
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        if len(self.nodes_info) < 2:
            self.skipTest('need at least 2 nodes')

        TestVmsAPI.nodeid = self.nodeid
        #for this setup storage node will be different from vm node
        TestVmsAPI.storage_node = self.get_random_node(except_node=self.nodeid)
        nodes = [TestVmsAPI.storage_node]
        number_of_free_disks, disk_type = self.get_max_available_free_disks(nodes)

        storageclusters = self.storageclusters_api.get_storageclusters()
        if not storageclusters.json():

            if not number_of_free_disks:
                self.skipTest('[*] No free disks to create storage cluster')

            self.lg.info('[*] Create storagecluster')
            response, cluster = self.storageclusters_api.post_storageclusters(nodes=nodes, driveType=disk_type, servers=1)
            self.assertEqual(response.status_code, 201)

            self.lg.info('[*] Storagecluster is created with specs : {}'.format(cluster))
            storagecluster = cluster['label']

        else:
            storagecluster = storageclusters.json()[0]

        self.lg.info('[*] Create vdiskstorage')
        response, vdiskstorage = self.vdisks_api.post_vdiskstorage(storagecluster=storagecluster)
        self.assertEqual(response.status_code, 201)

        self.lg.info('[*] Import image to vdiskstorage')
        response, imagedata = self.vdisks_api.post_import_image(vdiskstorageid=vdiskstorage['id'])
        self.assertEqual(response.status_code, 201)

        self.lg.info('[*] Import is imported with specs : {}'.format(imagedata))

        TestVmsAPI.vdiskstorageid = vdiskstorage['id']
        TestVmsAPI.imageid = imagedata["imageName"]
        TestVmsAPI.imageSize = imagedata["size"]
        TestVmsAPI.blockSize = imagedata["diskBlockSize"]

    @classmethod
    def tearDownClass(cls):
        self = cls()
        self.lg.info('[*] Delete image')
        self.vdisks_api.delete_image(TestVmsAPI.vdiskstorageid, TestVmsAPI.imageid)

    def setUp(self):
        super().setUp(except_node=TestVmsAPI.storage_node)
        response = self.nodes_api.get_nodes_nodeid_mem(self.nodeid)
        self.assertEqual(response.status_code, 200)
        node_available_memory = int(response.json()['available'] / (1024 ** 3))

        response = self.nodes_api.get_nodes_nodeid_cpus(self.nodeid)
        self.assertEqual(response.status_code, 200)
        node_available_cpus = len(response.json())

        self.lg.info('[*] Create ssh client contaienr')
        nics = [{"type": "default"}]
        response, self.ssh_client_data = self.containers_api.post_containers(self.nodeid, nics=nics, hostNetworking=True)
        self.assertEqual(response.status_code, 201)
        self.ssh_client = self.core0_client.get_container_client(self.ssh_client_data['name'])

        self.lg.info('[*] Create vdisk')
        vdisk_size = random.randint(TestVmsAPI.imageSize, TestVmsAPI.imageSize + 10)
        body = {"type": "boot", "size": vdisk_size, "blocksize": TestVmsAPI.blockSize, "readOnly": False}
        response, self.vdisk = self.vdisks_api.post_vdisks(vdiskstorageid=TestVmsAPI.vdiskstorageid, imageid=TestVmsAPI.imageid, **body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('[*] Vdisk disk is created with specs : {}'.format(self.vdisk))

        self.disks = [{"vdiskid": self.vdisk['id'], "maxIOps": 2000}]
        memory = random.randint(1, node_available_memory - 1) * 1024
        cpu = random.randint(1, node_available_cpus - 1)

        self.lg.info('[*] Create virtual machine (VM0) on node (N0)')
        nics = [{"type":"default"}]
        response, self.data = self.vms_api.post_nodes_vms(node_id=self.nodeid, memory=memory, cpu=cpu, nics=nics, disks=self.disks)
        self.assertEqual(response.status_code, 201)

        self.lg.info('[*] Virtual machine (VM0) is created with specs : {}'.format(self.data))

        response = self.vms_api.get_nodes_vms_vmid(nodeid=self.nodeid, vmid=self.data['id'])
        self.assertEqual(response.status_code, 200)

        self.lg.info('[*] Get virtual machine (VM0) default ip')
        self.vm_ip_address = self.get_vm_default_ipaddress(self.data['id'])

        time.sleep(20)

        self.lg.info('[*] Enable ssh access to virtual machine (VM0)')
        vm_vnc_port = response.json()['vnc'] - 5900
        vm_vnc_url = '{}:{}'.format(self.nodeip, vm_vnc_port)
        self.enable_ssh_access(vm_vnc_url)

    def tearDown(self):
        self.lg.info('[*] Delete virtual machine (VM0)')
        self.vms_api.delete_nodes_vms_vmid(self.nodeid, self.data['id'])

        self.lg.info('[*] Delete virtual disk (VD0)')
        self.vdisks_api.delete_vdisks_vdiskid(TestVmsAPI.vdiskstorageid, self.vdisk['id'])

        self.lg.info('[*] Delete ssh client contaienr')
        self.containers_api.delete_containers_containerid(self.nodeid, self.ssh_client_data['name'])

        super().tearDown()

    def setUp_vm_migration(self):
        self.lg.info('[*] Migrate virtual machine (VM0) to another node(N1), should succeed with 204')
        self.new_node = self.get_random_node(except_node=self.nodeid)
        self.new_node_client = self.Client(self.get_node_ip(self.new_node), password=self.jwt)
        body = {"nodeid": self.new_node}
        response = self.vms_api.post_nodes_vms_vmid_migrate(self.nodeid, self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('[*] Get virtual machine (VM0), virtual machine (VM0) status should be running ')
        response = self.vms_api.get_nodes_vms(self.new_node)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['id'], [x['id'] for x in response.json()])

        response = self.vms_api.get_nodes_vms_vmid(self.new_node, self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'running')

        response = self.vms_api.get_nodes_vms(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['id'], [x['id'] for x in response.json()])

        self.lg.info('[*] Create ssh client contaienr for new_node')
        nics = [{"type": "default"}]
        response, data = self.containers_api.post_containers(self.new_node, nics=nics, hostNetworking=True)
        self.assertEqual(response.status_code, 201)
        self.ssh_client2 = self.new_node_client.get_container_client(data['name'])

    @unittest.skip("https://github.com/zero-os/0-orchestrator/issues/1199")
    def test01_migrate_vm_more_than_one_time(self):
        """ GAT-156
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Migrate virtual machine (VM0) to another node(N1), should succeed with 204.
        #. Execute command on virtual machine (VM0), should succeed.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be running.
        #. Migrate virtual machine (VM0) to (N0) again, should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be running.
        #. Execute command on virtual machine (VM0), should succeed.

        """
        self.setUp_vm_migration()

        self.lg.info("Execute command on virtual machine (VM0), should succeed.")
        vm_ip_address = self.get_vm_default_ipaddress(self.data['id'], self.new_node)
        response = self.execute_command_inside_vm(self.ssh_client2, vm_ip_address, 'uname')
        self.assertEqual(response.state, 'SUCCESS')
        self.assertEqual(response.stdout.strip(), 'Linux')

        self.lg.info('[*] Migrate virtual machine (VM0) to (N0) again , should succeed with 204')
        body = {"nodeid": self.nodeid}
        response = self.vms_api.post_nodes_vms_vmid_migrate(self.new_node, self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('[*] Get virtual machine (VM0) in (N0) , virtual machine (VM0) status should be running ')
        response = self.vms_api.get_nodes_vms(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['id'], [x['id'] for x in response.json()])

        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'running')

        response = self.vms_api.get_nodes_vms(self.new_node)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['id'], [x['id'] for x in response.json()])

        self.lg.info("Execute command on virtual machine (VM0), should succeed.")
        vm_ip_address = self.get_vm_default_ipaddress(self.data['id'], self.nodeid)
        response = self.execute_command_inside_vm(self.ssh_client, vm_ip_address, 'uname')
        self.assertEqual(response.state, 'SUCCESS')
        self.assertEqual(response.stdout.strip(), 'Linux')

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1199')
    def test002_migration_afer_node_shutdown(self):
        """ GAT-167
        **Test Scenario:**

        #. Create virtual machine (VM0)'s storage components on node other than node N0
        #. Create the VM0 itself on node N0
        #. Migrate virtual machine (VM0) to node (N1), should succeed with 204.
        #. Get virtual machine (VM0), virtual machine (VM0) status should be running
        #. Shutdown node (N0) by leaving zerotier network, should succeed
        #. Make sure virtual machine (VM0) is running
        #. Execute command on virtual machine (VM0), should succeed.
        #. Make node (N0) join the zerotiernetwork again
        """

        self.setUp_vm_migration()

        self.lg.info('Shutdown node (N0) by leaving zerotier network, should succeed')
        node_pb_ip = self.core0_client.client.bash("ip -o a s dev enp2s0 | awk '{print $4}' | head -1 | awk -F/ '{print $1}'").get().stdout.split('\n')[0]
        try:
            if ipaddress.ip_address(node_pb_ip).is_private:
                self.skipTest("Private ip .. Can't run this testcase")
        except:
            self.skipTest("Can't get ip .. Most probably the interface name is wrong")
        zt_nid = self.core0_client.client.zerotier.list()[0]['id']
        try:
            self.core0_client.client.zerotier.leave(zt_nid)
        except:
            pass
        time.sleep(20)

        for i in range(60):
            time.sleep(1)
            if self.check_node_status(self.nodeid) == 'halted':
                break
        self.assertEqual(self.check_node_status(self.nodeid), 'halted')

        self.lg.info('Make sure VM0 is running')
        response = self.vms_api.get_nodes_vms_vmid(self.new_node, self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'running')

        self.lg.info("Execute command on virtual machine (VM0), should succeed.")
        vm_ip_address = self.get_vm_default_ipaddress(self.data['id'], self.new_node)
        response = self.execute_command_inside_vm(self.ssh_client2, vm_ip_address, 'uname')
        self.assertEqual(response.state, 'SUCCESS')
        self.assertEqual(response.stdout.strip(), 'Linux')

        self.lg.info('Make node (N0) join the zerotiernetwork again')
        client = Client(node_pb_ip, password=self.jwt)
        client.client.zerotier.join(zt_nid)
        for i in range(60):
            time.sleep(1)
            if self.check_node_status(self.nodeid) == 'running':
                break
        self.assertEqual(self.check_node_status(self.nodeid), 'running')
