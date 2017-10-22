import random, time
from testcases.testcases_base import TestcasesBase
import unittest


class Test_etcd(TestcasesBase):
    def setUp(self):
        super().setUp()
        number_of_free_disks, disk_type = self.get_max_available_free_disks([self.nodeid])
        storageclusters = self.storageclusters_api.get_storageclusters()

        if storageclusters.json() == []:
            if number_of_free_disks == []:
                self.skipTest(' [*] No free disks to create storagecluster')

            self.lg.info(' [*] Deploy new storage cluster (SC0)')
            response, data = self.storageclusters_api.post_storageclusters(
                nodes=[self.nodeid],
                driveType=disk_type,
                servers=random.randint(1, number_of_free_disks)
            )
            self.assertEqual(response.status_code, 201)
            self.storagecluster = data['label']

        else:
            self.storagecluster = storageclusters.json()[0]

        self.lg.info(' [*] Create vdiskstorage (VDS0)')
        response, self.vdiskstoragedata = self.vdisks_api.post_vdiskstorage(storagecluster=self.storagecluster)
        self.assertEqual(response.status_code, 201)

        self.lg.info(' [*] Import Image (IMG0) for (VDS0)')
        response, self.imagedata = self.vdisks_api.post_import_image(vdiskstorageid=self.vdiskstoragedata["id"])
        self.assertEqual(response.status_code, 201)

        self.lg.info(' [*] Create vdisk (VD0)')
        response, self.vdisk = self.vdisks_api.post_vdisks(vdiskstorageid=self.vdiskstoragedata["id"], imageid=self.imagedata["imageName"])
        self.assertEqual(response.status_code, 201)
        self.disks = [{"vdiskid": self.vdisk['id'], "maxIOps": 2000}]

        self.lg.info('[*]Get number of nodes (n)')
        self.number_of_nodes = len(self.nodes_info)

        self.lg.info('[*] Check that etcd process is running in n of nodes if n odd,and (n-1) of nodes if n even')
        self.nodes_with_etcd=[]
        for node in self.nodes_info:
            node_client = self.Client(node["ip"], password=self.jwt)
            response = node_client.client.bash("ps xu | grep [e]tcd").get()
            if response.state == "SUCCESS":
                self.nodes_with_etcd.append(node)
        if len(self.nodes_info)%2 == 0:
            self.lg.info("[*]number of nodes even")
            self.assertEqual(len(self.nodes_with_etcd), self.number_of_nodes-1)
        else:
            self.lg.info("[*]number of nodes odd")
            self.assertEqual(len(self.nodes_with_etcd), self.number_of_nodes)

    def test001_kill_etcdcluster_less_than_tolerance(self):
        """ GAT-150
        **Test Scenario:**

        #. Check that etcd process is running in all nodes if number of nodes odd.
        #. Check that etcd process is running in (n-1) nodes if number of nodes even.
        #. Kill etcd_cluster in less than or equal (n-1)/2 nodes ,should succeed.
        #. Check that etcd process return back in this nodes, should succeed.
        #. Create (VM0),should succeed.
        #. Get (VM0) details ,(VM0) status should be running.
        """
        self.lg.info(" Kill etcd_cluster in less than (n-1)/2 nodes")
        tolerance = int((len(self.nodes_with_etcd)-1)/2)
        for i in range(tolerance):
            node_client = self.Client(self.nodes_with_etcd[i]["ip"], password=self.jwt)
            response = node_client.client.bash("ps xu | grep [e]tcd | awk '{ print $1 }'").get()
            self.assertEqual(response.state, "SUCCESS")
            response = node_client.client.bash(" kill -9 %s"%response.stdout).get()
            self.assertEqual(response.state, "SUCCESS")

        self.lg.info(" Check that etcd process return back in this nodes, should succeed. ")
        for i in range(tolerance):
            for _ in range(5):
                time.sleep(5)
                node_client = self.Client(self.nodes_with_etcd[i]["ip"], password=self.jwt)
                response = node_client.client.bash("ps xu | grep [e]tcd | awk '{ print $1 }'").get()
                if response.stdout == " ":
                    continue
                break
            else:
                self.assertTrue(False, "etcd_cluster doesn't work again for node %s"%self.nodes_with_etcd[i]["id"])

        self.lg.info("Create (VM0),should succeed.")
        self.response, self.data = self.vms_api.post_nodes_vms(node_id=self.nodeid, disks=self.disks)
        self.assertEqual(self.response.status_code, 201)

        self.lg.info("Get (VM0) details ,(VM0) status should be running.")
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

    @unittest.skip("https://github.com/zero-os/0-orchestrator/issues/1196")
    def test002_kill_etcdcluster_more_than_tolerance(self):
        """ GAT-151
        **Test Scenario:**

        #. Check that etcd process run in all nodes if number of nodes odd.
        #. Check that etcd process run in (n-1) nodes if number of nodes even.
        #. kill etcd process in more than  (n-1)/2 nodes ,should succeed.
        #. Check that etcd process recovered in same numbers of nodes before killing etcd.
        #. Create (VM0),should succeed.
        #. Get (VM0) details ,(VM0) status should be running.
        """

        self.lg.info(" Kill etcd process in more than (n-1)/2 nodes")
        tolerance = int((len(self.nodes_with_etcd)-1)/2)
        for i in range(tolerance+1):
            node_client = self.Client(self.nodes_with_etcd[i]["ip"], password=self.jwt)
            response = node_client.client.bash("ps xu | grep [e]tcd | awk '{ print $1 }'").get()
            self.assertEqual(response.state, "SUCCESS")
            response = node_client.client.bash(" kill -9 %s"%response.stdout).get()
            self.assertEqual(response.state, "SUCCESS")

        self.lg.info(" Check that etcd process recovered in same numbers of nodes before killing etcd")
        recoverd_etcd = []
        for i in range(self.number_of_nodes):
            node_client = self.Client(self.nodes_info[i]["ip"], password=self.jwt)
            for _ in range(5):
                time.sleep(5)
                response = node_client.client.bash("ps xu | grep [e]tcd | grep [r]ecovered ").get()
                if "recovered" not in response.stdout:
                    continue
                recoverd_etcd.append(self.nodes_info[i])
                break

            if (len(recoverd_etcd) == len(self.nodes_with_etcd)):
                break
        else:
            self.assertEqual(len(recoverd_etcd), len(self.nodes_with_etcd))

        self.lg.info("Create (VM0),should succeed.")
        self.response, self.data = self.vms_api.post_nodes_vms(node_id=self.nodeid, memory=1024, cpu=1, disks=self.disks)
        self.assertEqual(self.response.status_code, 201)

        self.lg.info("Get (VM0) details ,(VM0) status should be running.")
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
