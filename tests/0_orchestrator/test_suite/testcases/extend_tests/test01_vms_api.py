import random, time, unittest
from testcases.testcases_base import TestcasesBase
from testcases.core0_client import Client
from parameterized import parameterized

class TestVmsAPI(TestcasesBase):
    @classmethod
    def setUpClass(cls):
        self = cls()
        super(TestVmsAPI, self).setUp()

        TestVmsAPI.nodeid = self.nodeid
        nodes = [TestVmsAPI.nodeid]
        number_of_free_disks, disk_type = self.get_max_available_free_disks(nodes)

        storageclusters = self.storageclusters_api.get_storageclusters()
        if not storageclusters.json():

            if not number_of_free_disks :
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
        super().setUp()

        response = self.nodes_api.get_nodes_nodeid_mem(self.nodeid)
        self.assertEqual(response.status_code, 200)
        node_available_memory = int(response.json()['available'] / (1024 ** 3))

        response = self.nodes_api.get_nodes_nodeid_cpus(self.nodeid)
        self.assertEqual(response.status_code, 200)
        node_available_cpus = len(response.json())

        self.lg.info('[*] Create ssh client contaienr')
        nics = [{"type":"default"}]
        response, self.ssh_client_data = self.containers_api.post_containers(self.nodeid, nics=nics, hostNetworking=True)
        self.assertEqual(response.status_code, 201)
        self.ssh_client = self.core0_client.get_container_client(self.ssh_client_data['name'])

        self.lg.info('[*] Create vdisk')
        vdisk_size = random.randint(TestVmsAPI.imageSize, TestVmsAPI.imageSize + 10)
        body = {"type": "boot", "size":vdisk_size, "blocksize":TestVmsAPI.blockSize, "readOnly": False}
        response, self.vdisk = self.vdisks_api.post_vdisks(vdiskstorageid=TestVmsAPI.vdiskstorageid, imageid=TestVmsAPI.imageid, **body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('[*] Vdisk disk is created with specs : {}'.format(self.vdisk))

        self.disks = [{"vdiskid": self.vdisk['id'], "maxIOps": 2000}]
        memory = random.randint(1, node_available_memory-1) * 1024
        cpu = random.randint(1, node_available_cpus-1)

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

    @unittest.skip("https://github.com/zero-os/0-orchestrator/issues/1199")
    def test01_migrate_vm_more_than_one_time(self, destination_node):
        """ GAT-156
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create virtual machine (VM0) on node (N0).
        #. Migrate virtual machine (VM0) to another node(N1), should succeed with 204.
        #. Get virtual machine (VM0) in (N1) , virtual machine (VM0) status should be running.
        #. Migrate virtual machine (VM0) to (N0) again, should succeed with 204.
        #. Get virtual machine (VM0) in (N0), virtual machine (VM0) status should be running.

        """

        self.lg.info('[*] List nodes.')
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        if len(self.nodes_info) < 2:
            self.skipTest('need at least 2 nodes')

        self.lg.info('[*] Migrate virtual machine (VM0) to another node(N1), should succeed with 204')
        new_node = self.get_random_node(except_node=self.nodeid)
        body = {"nodeid": new_node}
        response = self.vms_api.post_nodes_vms_vmid_migrate(self.nodeid, self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('[*] Get virtual machine (VM0) in (N1) , virtual machine (VM0) status should be running ')
        response = self.vms_api.get_nodes_vms(new_node)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['id'], [x['id'] for x in response.json()])

        response = self.vms_api.get_nodes_vms_vmid(new_node, self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'running')

        response = self.vms_api.get_nodes_vms(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['id'], [x['id'] for x in response.json()])

        self.lg.info('[*] Migrate virtual machine (VM0) to (N0) again , should succeed with 204')
        body = {"nodeid": self.nodeid}
        response = self.vms_api.post_nodes_vms_vmid_migrate(new_node, self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('[*] Get virtual machine (VM0) in (N0) , virtual machine (VM0) status should be running ')
        response = self.vms_api.get_nodes_vms(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['id'], [x['id'] for x in response.json()])

        response = self.vms_api.get_nodes_vms_vmid(self.nodeid, self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'running')

        response = self.vms_api.get_nodes_vms(new_node)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['id'], [x['id'] for x in response.json()])
