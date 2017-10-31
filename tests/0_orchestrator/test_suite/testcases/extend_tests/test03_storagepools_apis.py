import random
from testcases.testcases_base import TestcasesBase
import unittest
import time


class TestStoragepoolsAPI(TestcasesBase):

    def setUp(self):
        super().setUp()
        self.created_st_pools = []

    def setUp_storagepool(self, devices_no=None, **kwargs):
        self.freeDisks = [x['name'] for x in self.core0_client.getFreeDisks()]
        if self.freeDisks == []:
            self.skipTest(' [*] No free disks on node {}'.format(self.nodeid))

        self.lg.info(' [*] Create storagepool (SP0) on node (N0)')
        if not devices_no:
            if devices_no >= len(self.freeDisks):
                devices = random.sample(set(self.freeDisks), devices_no)
                self.response, self.data = self.storagepools_api.post_storagepools(node_id=self.nodeid,
                                                                                    free_devices=self.freeDisks, devices=devices, **kwargs)
            else:
                self.skipTest(' [*] No {} free disks on node {}'.format(devices_no, self.nodeid))
        else:
            self.response, self.data = self.storagepools_api.post_storagepools(node_id=self.nodeid,
                                                                                free_devices=self.freeDisks, **kwargs)
        self.assertEqual(self.response.status_code, 201)
        self.created_st_pools.append(self.data['name'])

    def tearDown(self):
        for st_pool in self.created_st_pools:
            self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, st_pool)
            super().tearDown()

    def setUp_plus_fileSystem(self, **kwargs):
        self.lg.info(' [*] Create filesystem (FS0) on storagepool {}'.format(self.data['name']))
        self.response_filesystem, self.data_filesystem = self.storagepools_api.post_storagepools_storagepoolname_filesystems(
            node_id=self.nodeid,
            storagepoolname=self.data['name'], **kwargs)
        self.assertEqual(self.response_filesystem.status_code, 201, " [*] Can't create filesystem on storagepool.")

    def setUp_plus_fileSystem_plus_snapShots(self):
        self.setUp_plus_fileSystem()
        self.lg.info(' [*] Create snapshot (SS0) of filesystem {}'.format(self.data_filesystem['name']))
        self.response_snapshot, self.data_snapshot = self.storagepools_api.post_filesystems_snapshots(self.nodeid,
                                                                                                      self.data['name'],
                                                                                                      self.data_filesystem[
                                                                                                          'name'])
        self.assertEqual(self.response_snapshot.status_code, 201, " [*] can't create new snapshot.")

    def def test001_create_storagepool_different_raids(self):
        """ GAT-000
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Create storagepool (SP0) on node (N0) with raid0 using 2 disks, should succeed.
        #. Check if two disks have been used for (SP0).
        #. Create storagepool (SP1) on node (N0) with raid0 using one disk, should fail.
        """

        self.lg.info('Create storagepool (SP0) on node (N0) with raid0 using 2 disks, should succeed.')
        self.setUp_storagepool(devices_no=2, metadataProfile='raid0', dataProfile='raid0')
        self.lg.info('Check if two disks have been used for (SP0).')
        self.lg.info('Create storagepool (SP1) on node (N0) with raid0 using one disk, should fail.')
