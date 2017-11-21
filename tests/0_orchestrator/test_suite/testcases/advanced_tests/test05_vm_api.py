import random, time, unittest
from testcases.testcases_base import TestcasesBase
from parameterized import parameterized

class AdvancedTestVmsAPI(TestcasesBase):
    @parameterized.expand([(0, 0)])
    def test014_vdisk_storage(self, limits, expeced_result):
        """ GAT-079
        **Test Scenario:**

        #. Create a new vdiskstorage on one disk
        #. Import an image
        #. Create a vdisk (VD1) storage with size equal to this disk size
        #. Create (VM1) on node (N0) and attach vdisk (VD1) to it. should succeed.
        #. Create a file with size equal to {limits} variable
        #. Check healthcheck status
        """

        self.nodes = self.get_running_nodes()
        for node in self.nodes:
            number_of_free_disks, disk_type = self.get_max_available_free_disks([node])
            if number_of_free_disks:
                break
        else:
            self.skipTest('[*] No free disks to create block cluster')

        print('[*] Get node disks info before creation')
        node_disks_info_before = self.get_node_free_disks_info(nodeid=node)

        print('[*] Create block cluster')
        response, cluster = self.storageclusters_api.post_storageclusters(nodes=[node], driveType=disk_type, servers=1)
        self.assertEqual(response.status_code, 201)

        print('[*] Get node disks info after creation')
        node_disks_info_after = self.get_node_free_disks_info(nodeid=node)

        print('[*] Get block cluster size')
        for disk_before in node_disks_info_before:
            for disk_after in node_disks_info_after:
                if disk_after['name'] == disk_before['name']:
                    break
            else:
                block_cluster_size = disk_before['size']
                print('block cluster size : %d' % block_cluster_size)
                break
        else:
            self.lg.error(' [*] There is an error!')

        print('[*] block cluster is created with specs : {}'.format(cluster))
        storagecluster = cluster['label']

        print('[*] Create vdiskstorage')
        response, vdiskstorage = self.vdisks_api.post_vdiskstorage(storagecluster=storagecluster)
        self.assertEqual(response.status_code, 201)

        print('[*] Import image to vdiskstorage')
        response, imagedata = self.vdisks_api.post_import_image(vdiskstorageid=vdiskstorage['id'])
        self.assertEqual(response.status_code, 201)

        print('[*] Image was imported with specs : {}'.format(imagedata))
        self.vdiskstorageid = vdiskstorage['id']
        self.imageid = imagedata["imageName"]
        self.imageSize = imagedata["size"]
        self.blockSize = imagedata["diskBlockSize"]

        response = self.nodes_api.get_nodes_nodeid_mem(self.nodeid)
        self.assertEqual(response.status_code, 200)
        node_available_memory = int(response.json()['available'] / (1024 ** 3))

        response = self.nodes_api.get_nodes_nodeid_cpus(self.nodeid)
        self.assertEqual(response.status_code, 200)
        node_available_cpus = len(response.json())

        print('[*] Create ssh client contaienr')
        nics = [{"type": "default"}]
        response, self.ssh_client_data = self.containers_api.post_containers(self.nodeid, nics=nics,
                                                                             hostNetworking=True)
        self.assertEqual(response.status_code, 201)
        self.ssh_client = self.core0_client.get_container_client(self.ssh_client_data['name'])

        print('[*] Create vdisk')
        body = {"type": "boot", "size": block_cluster_size, "blocksize": self.blockSize, "readOnly": False}
        response, self.vdisk = self.vdisks_api.post_vdisks(vdiskstorageid=self.vdiskstorageid,
                                                           imageid=self.imageid, **body)
        self.assertEqual(response.status_code, 201)

        print('[*] Vdisk disk is created with specs : {}'.format(self.vdisk))

        self.disks = [{"vdiskid": self.vdisk['id'], "maxIOps": 2000}]
        memory = random.randint(1, node_available_memory - 1) * 1024
        cpu = random.randint(1, node_available_cpus - 1)

        print('[*] Create virtual machine (VM0) on node (N0)')
        nics = [{"type": "default"}]
        response, self.data = self.vms_api.post_nodes_vms(node_id=self.nodeid, memory=memory, cpu=cpu, nics=nics,
                                                          disks=self.disks)
        self.assertEqual(response.status_code, 201)

        print('[*] Virtual machine (VM0) is created with specs : {}'.format(self.data))

        response = self.vms_api.get_nodes_vms_vmid(nodeid=self.nodeid, vmid=self.data['id'])
        self.assertEqual(response.status_code, 200)

        print('[*] Get virtual machine (VM0) default ip')
        self.vm_ip_address = self.get_vm_default_ipaddress(self.data['id'])

        time.sleep(20)

        print('[*] Enable ssh access to virtual machine (VM0)')
        vm_vnc_port = response.json()['vnc'] - 5900
        vm_vnc_url = '{}:{}'.format(self.nodeip, vm_vnc_port)
        self.enable_ssh_access(vm_vnc_url)

        """TODO
            Write File
            Check health check api
        """