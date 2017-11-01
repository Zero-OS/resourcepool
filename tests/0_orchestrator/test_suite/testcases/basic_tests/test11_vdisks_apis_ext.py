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

        self.lg.info(' [*] Delete Vdiskstorage (VD0)')
        self.vdisks_api.delete_vdiskstorage(self.vdiskstoragedata["id"])
        super(TestVdisks, self).tearDown()

    def test001_create_two_vdiskstorage_with_same_name(self):
        """ GAT-147
        **Test Scenario:**

        #. Create vdiskstorage(vds0).
        #. Create vdiskstorage(vds1) with same name as vds1, should fail with 409 conflict.
        #. Create Vdiskstorage(vds2)with non exist storagecluster , should fail 400 not found
        """
        self.lg.info("Create vdiskstorage (vds1) with same name as vds1,should return 409")
        vds1_name = self.vdiskstoragedata["id"]
        response, data = self.vdisks_api.post_vdiskstorage(storagecluster=self.storagecluster, id=vds1_name)
        self.assertEqual(response.status_code, 409)

        self.lg.info("Create Vdiskstorage(vds2)with non exist storagecluster , should return 400")
        fake_storagecluster = self.rand_str()
        response, data = self.vdisks_api.post_vdiskstorage(storagecluster=fake_storagecluster, id=vds1_name)
        self.assertEqual(response.status_code, 400)

    @unittest.skip("https://github.com/zero-os/0-orchestrator/issues/1148")
    def test002_create_images(self):
        """ GAT-148
        **Test Scenario:**

        #. create Vdiskstorage(VDS0).
        #. Import image(IMG0)for (VDS0).
        #. Import image(IMG1)for (VDS0) with same name as (IMG0) ,should fail with 409 conflict.
        #. Create vdiskstorage(VDS1).
        #. Get list of images in VDS0,(IMG0) only should be there.
        #. Get list of images in VDS1,(IMG0) should not be there.
        """

        self.lg.info('Import image(IMG1)for (VDS0) with same name as (IMG0) ,should fail with 409 conflict.')
        response, imagedata = self.vdisks_api.post_import_image(vdiskstorageid=self.vdiskstoragedata["id"],
                                                                imageName=self.imagedata["imageName"])
        self.assertEqual(response.status_code, 409)

        self.lg.info('Create vdiskstorage(VDS1).')
        response, vdse1_data = self.vdisks_api.post_vdiskstorage(storagecluster=self.storagecluster)
        self.assertEqual(response.status_code, 201)

        self.lg.info('Get list of images in VDS0,(IMG0) only should be there')
        response = self.vdisks_api.get_import_images(self.vdiskstoragedata["id"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        response = self.vdisks_api.get_image_info(self.vdiskstoragedata["id"], self.imagedata["imageName"])
        self.assertEqual(response.status_code, 200)

        self.lg.info(' Get list of images in VDS1,(IMG1) and (IMG0) should not be there')
        response = self.vdisks_api.get_image_info(vdse1_data["id"], self.imagedata["imageName"])
        self.assertEqual(response.status_code, 404)

    def test003_create_differnet_vdisks(self):
        """ GAT-149
        **Test Scenario:**

        #. Create VdiskStorage(vds0)
        #. Import Image(IMG0)
        #. Create vdisk (vdisk0) with IMG0, should succeed
        #. Creare vdisk(vdisk1) with IMG0,should succeed
        #. Create vdisk(vdisk2) with same name as vdisk2, should fail
        #. Creare vdisk(vdisk3) with non-exist image ,should fail

        """

        self.lg.info('Creare vdisk(vdisk1) with IMG0,should succeed.')
        response, vdisk1_data = self.vdisks_api.post_vdisks(vdiskstorageid=self.vdiskstoragedata["id"], imageid=self.imagedata["imageName"])
        self.assertEqual(response.status_code, 201)

        self.lg.info('Create vdisk(vdisk2) with same name as vdisk2, should fail')
        response, vdisk2_data = self.vdisks_api.post_vdisks(vdiskstorageid=self.vdiskstoragedata["id"],
                                                            imageid=self.imagedata["imageName"],
                                                            id=vdisk1_data["id"])
        self.assertEqual(response.status_code, 409)

        self.lg.info('Creare vdisk(vdisk3) with non-exist image ,should fail')
        fake_image = self.rand_str()
        response, vdisk3_data = self.vdisks_api.post_vdisks(vdiskstorageid=self.vdiskstoragedata["id"],
                                                            imageid=fake_image, type="boot")
        self.assertEqual(response.status_code, 400)
