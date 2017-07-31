import random, time
from testcases.testcases_base import TestcasesBase
import unittest


class TestVdisks(TestcasesBase):
    def setUp(self):
        super().setUp()
        free_disks = self.core0_client.getFreeDisks()
        if free_disks == []:
            self.skipTest(' [*] No free disks to create storagecluster')

        storageclusters = self.storageclusters_api.get_storageclusters()
        if storageclusters.json() == []:
            self.lg.info(' [*] Deploy new storage cluster (SC0)')
            response, data = self.storageclusters_api.post_storageclusters(node_id=self.nodeid,
                                                                           servers=random.randint(1, len(free_disks)))
            self.assertEqual(response.status_code, 201)
            self.storagecluster = data['label']
        else:
            self.storagecluster = storageclusters.json()[0]

        self.lg.info(' [*] Create vdisk (VD0)')
        self.response, self.data = self.vdisks_api.post_vdisks(storagecluster=self.storagecluster)
        self.assertEqual(self.response.status_code, 201)

    def tearDown(self):
        self.lg.info(' [*] Delete vdisk (VD0)')
        self.vdisks_api.delete_vdisks_vdiskid(self.data['id'])
        super(TestVdisks, self).tearDown()

    def test001_get_vdisk_details(self):
        """ GAT-061
        *GET:/vdisks/{vdiskid}*

        **Test Scenario:**

        #. Create vdisk (VD0).
        #. Get vdisk (VD0), should succeed with 200.
        #. Get nonexisting vdisk, should fail with 404.

        """
        self.lg.info(' [*] Get vdisk (VD0), should succeed with 200')
        response = self.vdisks_api.get_vdisks_vdiskid(self.data['id'])
        self.assertEqual(response.status_code, 200)
        for key in self.data.keys():
            if not self.data['readOnly']:
                continue
            self.assertEqual(self.data[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'halted')

        self.lg.info(' [*] Get nonexisting vdisk, should fail with 404')
        response = self.vdisks_api.get_vdisks_vdiskid(self.rand_str())
        self.assertEqual(response.status_code, 404)

    def test002_list_vdisks(self):
        """ GAT-062
        *GET:/vdisks*

        **Test Scenario:**

        #. Create vdisk (VD0).
        #. List vdisks, should succeed with 200.

        """
        self.lg.info(' [*] List vdisks, should succeed with 200')
        response = self.vdisks_api.get_vdisks()
        self.assertEqual(response.status_code, 200)
        vd0_data = {"id": self.data['id'],
                    "storageCluster": self.data['storagecluster'],
                    "type": self.data['type']}
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
        self.lg.info(' [*] List vdisks, (VD1) should be listed')
        response = self.vdisks_api.get_vdisks()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['id'], [x['id'] for x in response.json()])

        self.lg.info(' [*] Delete vdisk (VD0), should succeed with 204')
        response = self.vdisks_api.delete_vdisks_vdiskid(self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Create vdisk with invalid body, should fail with 400')
        body = {"id": self.rand_str()}
        response, data = self.vdisks_api.post_vdisks(body)
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
        self.lg.info(' [*] Delete vdisk (VD0), should succeed with 204')
        response = self.vdisks_api.delete_vdisks_vdiskid(self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List vdisks, (VD0) should be gone')
        response = self.vdisks_api.get_vdisks()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['id'], [x['id'] for x in response.json()])

        self.lg.info(' [*] Delete nonexisting vdisk, should fail with 404')
        response = self.vdisks_api.delete_vdisks_vdiskid('fake_vdisk')
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
        self.lg.info(' [*] Resize vdisk (VD0), should succeed with 204')
        new_size = self.data['size'] + random.randint(1, 10)
        body = {"newSize": new_size}
        response = self.vdisks_api.post_vdisks_vdiskid_resize(self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that size of volume changed, should succeed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_size, response.json()['size'])
        self.size = new_size

        self.lg.info(' [*] Resize vdisk (VD0) with value less than the current vdisk size, should fail with 400')
        new_size = self.size - random.randint(1, self.size - 1)
        body = {"newSize": new_size}
        response = self.vdisks_api.post_vdisks_vdiskid_resize(self.data['id'], body)
        self.assertEqual(response.status_code, 400)

        self.lg.info(' [*] Check vdisk (VD0) size, shouldn\'t be changed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.data['id'])
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

        self.lg.info(' [*]  Resize  created volume.')
        new_size = self.size + random.randint(1, 10)
        body = {"newSize": new_size}
        response = self.vdisks_api.post_volumes_volumeid_resize(self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that size of volume changed, should succeed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_size, response.json()['size'])

        self.lg.info(' [*] Rollback vdisk (VD0), should succeed')
        body = {"epoch": self.vd_creation_time}
        response = self.vdisks_api.post_vdisks_vdiskid_rollback(self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that vdisk (VD0) size is changed to the initial size, should succeed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.size, response.json()['size'])
