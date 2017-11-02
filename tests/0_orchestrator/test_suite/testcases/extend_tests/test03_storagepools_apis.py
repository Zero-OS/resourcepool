import random
from testcases.testcases_base import TestcasesBase
from parameterized import parameterized
import unittest
import time


class TestStoragepoolsAPI(TestcasesBase):

    def setUp(self):
        super().setUp()
        self.created_st_pools = []

    def setUp_storagepool(self, res_status, devices_no=None, **kwargs):
        self.freeDisks = [x['name'] for x in self.core0_client.getFreeDisks()]
        if self.freeDisks == []:
            self.skipTest(' [*] No free disks on node {}'.format(self.nodeid))

        if devices_no:
            if devices_no <= len(self.freeDisks):
                devices = random.sample(set(self.freeDisks), devices_no)
                self.response, self.data = self.storagepools_api.post_storagepools(node_id=self.nodeid,
                                                                                    free_devices=self.freeDisks, devices=devices, **kwargs)
            else:
                self.skipTest(' [*] No {} free disks on node {}'.format(devices_no, self.nodeid))
        else:
            self.response, self.data = self.storagepools_api.post_storagepools(node_id=self.nodeid,
                                                                                free_devices=self.freeDisks, **kwargs)
        self.assertEqual(self.response.status_code, res_status)
        if self.response.status_code == 201:
            self.created_st_pools.append(self.data['name'])

    def tearDown(self):
        self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, self.created_st_pools[0])
        self.created_st_pools.remove(self.created_st_pools[0])
        super().tearDown()

    @parameterized.expand([('raid0', 2), ('raid1', 2), ('raid5', 2), ('raid6', 3), ('raid10', 4), ('dup', 1)])
    def test001_create_storagepool_different_raids(self, profile, devices_no):
        """ GAT-166
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Create storagepool (SP1) on node (N0) with raid0 using one disk, should fail.
        #. Create storagepool (SP0) on node (N0) with different raids, should succeed.
        #. Check if two disks have been used for (SP0).
        """

        self.lg.info('Create storagepool (SP1) on node (N0) with raid0 using one disk, should fail.')
        self.setUp_storagepool(res_status=500, devices_no=devices_no - 1, metadataProfile=profile, dataProfile=profile)

        self.lg.info('Create storagepool (SP0) on node (N0) with {} using {} disks, should succeed.'.format(profile, devices_no))
        self.setUp_storagepool(res_status=201, devices_no=devices_no, metadataProfile=profile, dataProfile=profile)

        exp = "cut -d ':' -f 1 | cut -d ' ' -f 2"
        res = self.core0_client.client.bash("btrfs filesystem df /mnt/storagepools/{} | grep Data | {}".format(self.data['name'], exp)).get().stdout.strip('\n')
        self.assertEqual(profile, res.lower())
        res = self.core0_client.client.bash("btrfs filesystem df /mnt/storagepools/{} | grep Metadata | {}".format(self.data['name'], exp)).get().stdout.strip('\n')
        self.assertEqual(profile, res.lower())

        self.lg.info('Check if {} disks have been used for (SP0).'.format(devices_no))
        devices = [b['total_devices'] for b in self.core0_client.client.btrfs.list() if b['label'] == 'sp_' + self.data['name']]
        self.assertEqual(devices[0], devices_no)
