import random, time
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.orchestrator_api.orchestrator_client.vdisks_apis import VDisksAPIs
from api_testing.orchestrator_api.orchestrator_client.storageclusters_apis import Storageclusters
from api_testing.utiles.core0_client import Client
import unittest

# @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/644')
class TestVdisks(TestcasesBase):

    def setUp(self):
        super().setUp()
        self.vdisks_apis = VDisksAPIs()
        self.storageclusters_api = Storageclusters()

        node = self.get_random_node()
        pyclient_ip = [x['ip'] for x in self.nodes if x['id'] == node][0]
        self.jwt = self.nodes_api.jwt
        self.pyclient = Client(pyclient_ip, password=self.jwt)

        free_disks = self.pyclient.getFreeDisks()
        if free_disks == []:
            self.skipTest('no free disks to create storagecluster')

        storageclusters = self.storageclusters_api.get_storageclusters()
        if storageclusters.json() == []:
            self.lg.info('Deploy new storage cluster (SC0)')
            sc_label = self.rand_str()
            sc_servers = random.randint(1, len(free_disks))
            sc_drivetype = 'ssd'
            sc_nodes = [node]
            sc_body = {"label": sc_label,
                        "servers": sc_servers,
                        "driveType": sc_drivetype,
                        "clusterType": "storage",
                        "nodes":sc_nodes}

            response = self.storageclusters_api.post_storageclusters(sc_body)
            self.assertEqual(response.status_code, 201)

            for _ in range(60):
                response = self.storageclusters_api.get_storageclusters_label(sc_label)
                if response.status_code == 200:
                    if response.json()['status'] == 'ready':
                        break
                    else:
                        time.sleep(3)
                else:
                    time.sleep(10)
            else:
                self.lg.error('storagecluster status is not ready after 180 sec')

        else:
            sc_label = storageclusters.json()[0]

        self.lg.info('Create vdisk (VD0)')
        self.vd_creation_time = time.time()
        self.vdisk_id = self.rand_str()
        self.size = random.randint(1, 50)
        self.types = ['boot','db','cache','tmp']
        self.type = random.choice(self.types)
        self.block_size = random.randint(1, self.size)*512
        self.storagecluster = sc_label
        self.readOnly = random.choice([False, True])

        self.body = {"id": self.vdisk_id,
                     "size": self.size,
                     "blocksize": self.block_size,
                     "type": self.type,
                     "storagecluster": self.storagecluster,
                     "readOnly":self.readOnly}

        response = self.vdisks_apis.post_vdisks(self.body)
        self.assertEqual(response.status_code, 201) 

    def tearDown(self):
        self.lg.info('Delete vdisk (VD0)')
        self.vdisks_apis.delete_vdisks_vdiskid(self.vdisk_id)
        super(TestVdisks, self).tearDown()

    def test001_get_vdisk_details(self):
        """ GAT-061
        *GET:/vdisks/{vdiskid}*

        **Test Scenario:**

        #. Create vdisk (VD0).
        #. Get vdisk (VD0), should succeed with 200.
        #. Get nonexisting vdisk, should fail with 404.

        """
        self.lg.info('Get vdisk (VD0), should succeed with 200')
        response = self.vdisks_apis.get_vdisks_vdiskid(self.vdisk_id)
        self.assertEqual(response.status_code, 200)
        for key in self.body.keys():
            if not self.readOnly and key == "readOnly":
                continue
            self.assertEqual(self.body[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'halted')

        self.lg.info('Get nonexisting vdisk, should fail with 404')
        response = self.vdisks_apis.get_vdisks_vdiskid('fake_vdisk')
        self.assertEqual(response.status_code, 404)

    def test002_list_vdisks(self):
        """ GAT-062
        *GET:/vdisks*

        **Test Scenario:**

        #. Create vdisk (VD0).
        #. List vdisks, should succeed with 200.

        """
        self.lg.info('List vdisks, should succeed with 200')
        response = self.vdisks_apis.get_vdisks()
        self.assertEqual(response.status_code, 200)
        vd0_data = {"id": self.vdisk_id,
                    "storageCluster": self.storagecluster,
                    "type": self.type}
        self.assertIn(vd0_data, response.json())

    def test003_create_vdisk(self):
        """ GAT-063
        *POST:/vdisks*

        **Test Scenario:**

        #. Create vdisk (VD1). should succeed with 201.
        #. List vdisks, (VD1) should be listed.
        #. Delete vdisk (VD0), should succeed with 204.
        #. Create vdisk with invalid body, should fail with 400.
        """
        self.lg.info('Create vdisk (VD1). should succeed with 201')
        vdisk_id = self.rand_str()
        size = random.randint(1, 50)
        vdisk_type = random.choice(self.types)
        block_size = random.randint(1, self.size)*512
        readOnly = random.choice([False, True])

        body = {"id": vdisk_id,
                "size": size,
                "blocksize": block_size,
                "type": vdisk_type,
                "storagecluster": self.storagecluster,
                "readOnly":readOnly}

        response = self.vdisks_apis.post_vdisks(body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('List vdisks, (VD1) should be listed')
        response = self.vdisks_apis.get_vdisks()
        self.assertEqual(response.status_code, 200)
        self.assertIn(vdisk_id, [x['id'] for x in response.json()])

        self.lg.info('Delete vdisk (VD0), should succeed with 204')
        response = self.vdisks_apis.delete_vdisks_vdiskid(self.vdisk_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Create vdisk with invalid body, should fail with 400')
        body = {"id":self.rand_str()}
        response = self.vdisks_apis.post_vdisks(body)
        self.assertEqual(response.status_code, 400)


    def test004_delete_vdisk(self):
        """ GAT-064
        *Delete:/vdisks/{vdiskid}*

        **Test Scenario:**

        #. Create vdisk (VD0).
        #. Delete vdisk (VD0), should succeed with 204.
        #. List vdisks, (VD0) should be gone.
        #. Delete nonexisting vdisk, should fail with 404.
        """
        self.lg.info('Delete vdisk (VD0), should succeed with 204')
        response = self.vdisks_apis.delete_vdisks_vdiskid(self.vdisk_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info('List vdisks, (VD0) should be gone')
        response = self.vdisks_apis.get_vdisks()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.vdisk_id, [x['id'] for x in response.json()])

        self.lg.info('Delete nonexisting vdisk, should fail with 404')
        response = self.vdisks_apis.delete_vdisks_vdiskid('fake_vdisk')
        self.assertEqual(response.status_code, 404)

    def test005_resize_vdisk(self):
        """ GAT-065
        *POST:/vdisks/{vdiskid}/resize*

        **Test Scenario:**

        #. Create vdisk (VD0).
        #. Resize vdisk (VD0), should succeed with 204.
        #. Check that size of volume changed, should succeed.
        #. Resize vdisk (VD0) with value less than the current vdisk size, should fail with 400.
        #. Check vdisk (VD0) size, shouldn't be changed.

        """
        self.lg.info('Resize vdisk (VD0), should succeed with 204')
        new_size = self.size + random.randint(1,10)
        body = {"newSize": new_size}
        response = self.vdisks_apis.post_vdisks_vdiskid_resize(self.vdisk_id, body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that size of volume changed, should succeed')
        response = self.vdisks_apis.get_vdisks_vdiskid(self.vdisk_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_size, response.json()['size'])
        self.size = new_size

        self.lg.info('Resize vdisk (VD0) with value less than the current vdisk size, should fail with 400')
        new_size = self.size - random.randint(1, self.size-1)
        body = {"newSize": new_size}
        response = self.vdisks_apis.post_vdisks_vdiskid_resize(self.vdisk_id, body)
        self.assertEqual(response.status_code, 400)

        self.lg.info('Check vdisk (VD0) size, shouldn\'t be changed')
        response = self.vdisks_apis.get_vdisks_vdiskid(self.vdisk_id)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(new_size, response.json()['size'])


    @unittest.skip('Not implemented')
    def test006_Rollback_vdisk(self):
        """ GAT-066
        *POST:/vdisks/{vdiskid}/rollback*

        **Test Scenario:**

        #. Create vdisk (VD0), should succeed.
        #. Resize vdisk (VD0), should succeed.
        #. Check that size of vdisk (VD0) changed, should succeed.
        #. Rollback vdisk (VD0), should succeed.
        #. Check that vdisk (VD0) size is changed to the initial size, should succeed.
        """

        self.lg.info(' Resize  created volume.')
        new_size = self.size + random.randint(1, 10)
        body = {"newSize": new_size}
        response = self.vdisks_apis.post_volumes_volumeid_resize(self.vdisk_id, body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that size of volume changed, should succeed')
        response = self.vdisks_apis.get_vdisks_vdiskid(self.vdisk_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_size, response.json()['size'])

        self.lg.info('Rollback vdisk (VD0), should succeed')
        body = {"epoch": self.vd_creation_time}
        response = self.vdisks_apis.post_vdisks_vdiskid_rollback(self.vdisk_id, body)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Check that vdisk (VD0) size is changed to the initial size, should succeed')
        response = self.vdisks_apis.get_vdisks_vdiskid(self.vdisk_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.size, response.json()['size'])
