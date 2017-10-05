import random, time
from testcases.testcases_base import TestcasesBase
import unittest


class TestVdisks(TestcasesBase):
    def setUp(self):
        super().setUp()
        nodes = [self.nodeid]
        number_of_free_disks, disk_type = self.get_max_available_free_disks(nodes)
        storageclusters = self.storageclusters_api.get_storageclusters()
        if storageclusters.json() == []:
            if number_of_free_disks == []:
                self.skipTest(' [*] No free disks to create storagecluster')

            self.lg.info(' [*] Deploy new storage cluster (SC0)')
            response, data = self.storageclusters_api.post_storageclusters(
                nodes=nodes,
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
        response, self.data = self.vdisks_api.post_vdisks(vdiskstorageid=self.vdiskstoragedata["id"], imageid=self.imagedata["imageName"])
        self.assertEqual(response.status_code, 201)

    def tearDown(self):
        self.lg.info(' [*] Delete vdisk (VD0)')
        self.vdisks_api.delete_vdisks_vdiskid(self.vdiskstoragedata["id"], self.data['id'])

        self.lg.info(' [*] Delete Image (IMG0)')
        self.vdisks_api.delete_image(self.vdiskstoragedata["id"], self.imagedata['imageName'])
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
        response = self.vdisks_api.get_vdisks_vdiskid(self.vdiskstoragedata["id"], self.data['id'])
        self.assertEqual(response.status_code, 200)
        for key in self.data.keys():
            if key in list(response.json().keys()):
                self.assertEqual(self.data[key], response.json()[key])
        self.assertEqual(response.json()['status'], 'halted')

        self.lg.info(' [*] Get nonexisting vdisk, should fail with 404')
        response = self.vdisks_api.get_vdisks_vdiskid(self.vdiskstoragedata["id"], self.rand_str())
        self.assertEqual(response.status_code, 404)

    def test002_list_vdisks(self):
        """ GAT-062
        *GET:/vdisks*

        **Test Scenario:**

        #. Create vdisk (VD0).
        #. List vdisks, should succeed with 200.

        """
        self.lg.info(' [*] List vdisks, should succeed with 200')
        response = self.vdisks_api.get_vdisks(self.vdiskstoragedata["id"])
        self.assertEqual(response.status_code, 200)
        vd0_data = {"id": self.data['id'],
                    "vdiskstorage": self.vdiskstoragedata["id"],
                    "type": self.data['type']
                    }
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
        response = self.vdisks_api.get_vdisks(self.vdiskstoragedata["id"])
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['id'], [x['id'] for x in response.json()])

        self.lg.info(' [*] Delete vdisk (VD0), should succeed with 204')
        response = self.vdisks_api.delete_vdisks_vdiskid(self.vdiskstoragedata["id"], self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Create vdisk with invalid body, should fail with 400')
        body = {"id": self.rand_str(),"type":"cash", "imageId":self.imagedata["imageName"]}
        response, data= self.vdisks_api.post_vdisks(vdiskstorageid=self.vdiskstoragedata["id"],** body)
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
        response = self.vdisks_api.delete_vdisks_vdiskid(self.vdiskstoragedata["id"], self.data['id'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List vdisks, (VD0) should be gone')
        response = self.vdisks_api.get_vdisks(self.vdiskstoragedata["id"])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['id'], [x['id'] for x in response.json()])

        self.lg.info(' [*] Delete nonexisting vdisk, should fail with 404')
        response = self.vdisks_api.delete_vdisks_vdiskid(self.vdiskstoragedata["id"], 'fake_vdisk')
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
        current_size = self.data['size']
        new_size = current_size + random.randint(1, 10)
        body = {"newSize": new_size}
        response = self.vdisks_api.post_vdisks_vdiskid_resize(self.vdiskstoragedata["id"],self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that size of volume changed, should succeed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.vdiskstoragedata["id"],self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_size, response.json()['size'])
        current_size = new_size

        self.lg.info(' [*] Resize vdisk (VD0) with value less than the current vdisk size, should fail with 400')
        new_size = current_size - random.randint(1, current_size - 1)
        body = {"newSize": new_size}
        response = self.vdisks_api.post_vdisks_vdiskid_resize(self.vdiskstoragedata["id"],self.data['id'], body)
        self.assertEqual(response.status_code, 400)

        self.lg.info(' [*] Check vdisk (VD0) size, shouldn\'t be changed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.vdiskstoragedata["id"],self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(new_size, response.json()['size'])

    @unittest.skip('https://github.com/gig-projects/org_quality/issues/689')
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
        epoch = int(time.time())

        self.lg.info(' [*]  Resize  created volume.')
        current_size = self.data['size']
        new_size = current_size + random.randint(1, 10)
        body = {"newSize": new_size}
        response = self.vdisks_api.post_vdisks_vdiskid_resize(self.vdiskstoragedata["id"],self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that size of volume changed, should succeed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.vdiskstoragedata["id"],self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_size, response.json()['size'])

        self.lg.info(' [*] Rollback vdisk (VD0), should succeed')
        body = {"epoch": epoch}
        response = self.vdisks_api.post_vdisks_vdiskid_rollback(self.vdiskstoragedata["id"],self.data['id'], body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Check that vdisk (VD0) size is changed to the initial size, should succeed')
        response = self.vdisks_api.get_vdisks_vdiskid(self.vdiskstoragedata["id"],self.data['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_size, response.json()['size'])

    def test007_list_vdiskstorage(self):
        """ GAT-143
        *GET:/vdiskstorage*

        **Test Scenario:**

        #. Create vdiskstorage (VDS0).
        #. List vdisksStorage, should succeed with 200.

        """
        self.lg.info(' [*] List vdisksStorage, should succeed with 200')
        response = self.vdisks_api.get_vdiskstorage()
        self.assertEqual(response.status_code, 200)
        svd0_data = {"id": self.vdiskstoragedata['id'],
                     "blockCluster": self.vdiskstoragedata['blockCluster'],
                     "objectCluster": '',
                     "slaveCluster": ''}
        self.assertIn(svd0_data, response.json())

    @unittest.skip("https://github.com/zero-os/0-orchestrator/issues/1148")
    def test008_list_vdisk_images(self):
        """ GAT-144
        *GET:/vdisks_Images*

        **Test Scenario:**

        #. Create vdiskstorage (VDS0).
        #. Import Image IMG0.
        #. List all vdiskstorage images, should succeed with 200.

        """
        self.lg.info(' [*] List all vdiskstorage Images, should succeed with 200')
        response = self.vdisks_api.get_import_images(self.vdiskstoragedata["id"])
        self.assertEqual(response.status_code, 200)
        img0_data = {"name": self.imagedata["imageName"],
                     "size": self.imagedata['size'],
                     "diskBlockSize":  self.imagedata['diskBlockSize']
                     }
        self.assertIn(img0_data, response.json())

    def test009_get_vdiskstorage_details(self):
        """ GAT-145
        *GET:/vdiskstorage/{vdiskstorageid}*

        **Test Scenario:**

        #. Create vdiskstorage (VDS0).
        #. Get vdiskstorage (VDS0), should succeed with 200.
        #. Get nonexisting vdiskstorage, should fail with 404.

        """
        self.lg.info(' [*] Get vdisk (VDS0), should succeed with 200')
        response = self.vdisks_api.get_vdiskstorage_info(self.vdiskstoragedata["id"])
        self.assertEqual(response.status_code, 200)
        for key in self.vdiskstoragedata.keys():
            if key in list(response.json().keys()):
                self.assertEqual(self.vdiskstoragedata[key], response.json()[key])
        self.lg.info(' [*] Get nonexisting vdiskstorage, should fail with 404')
        response = self.vdisks_api.get_vdiskstorage_info(self.rand_str())
        self.assertEqual(response.status_code, 404)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/808')
    def test010_get_Imported_Image_details(self):
        """ GAT-146
        *GET:/vdiskstorage/{vdiskstorageid}*

        **Test Scenario:**

        #. Create vdiskstorage (VDS0).
        #.  Import Image IMG0.
        #. Get Imported Image(IMG0), should succeed with 200.
        #. Get nonexisting image, should fail with 404.

        """

        self.lg.info('Get Imported Image(IMG0), should succeed with 200.')
        response = self.vdisks_api.get_image_info(self.vdiskstoragedata["id"], self.imagedata["imageName"])
        self.assertEqual(response.status_code, 200)
        for key in self.imagedata.keys():
            if key in list(response.json().keys()):
                self.assertEqual(self.imagedata[key], response.json()[key])

        self.lg.info(' [*] Get nonexisting image, should fail with 404')
        fake_image = self.rand_str()
        response = self.vdisks_api.get_image_info(self.vdiskstoragedata["id"], fake_image)
        self.assertEqual(response.status_code, 404)
