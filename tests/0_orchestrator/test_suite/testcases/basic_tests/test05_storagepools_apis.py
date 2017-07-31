import random
from testcases.testcases_base import TestcasesBase
import unittest, time


class TestStoragepoolsAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.freeDisks = self.core0_client.getFreeDisks()
        if self.freeDisks == []:
            self.skipTest(' [*] No free disks on node {}'.format(self.nodeid))

        self.lg.info(' [*] Create storagepool (SP0) on node (N0)')
        self.response, self.data = self.storagepools_api.post_storagepools(node_id=self.nodeid,
                                                                           free_devices=self.freeDisks)
        self.assertEqual(self.response.status_code, 201)

        if self.id().split('.')[2] in ['test009_get_storagepool_filessystem', 'test010_list_storagepool_filesystems',
                                       'test011_post_storagepool_filesystem', 'test012_delete_storagepool_filesystem']:
            self.setUp_plus_fileSystem()
        elif self.id().split('.')[2] in ['test013_get_storagepool_filessystem_snapshot',
                                         'test014_list_storagepool_filesystems_snapshots',
                                         'test015_post_storagepool_filesystem_snapshot',
                                         'test016_delete_storagepool_filesystem_snapshot']:
            self.setUp_plus_fileSystem_plus_snapShots()

    def tearDown(self):
        response = self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, self.data['name'])
        self.assertEqual(response, 204, " [*]  Can't delete the storagepool")
        super().tearDown()

    def setUp_plus_fileSystem(self):
        self.lg.info(' [*] Create filesystem (FS0) on storagepool {}'.format(self.data['name']))
        self.response_filesystem, self.data_filesystem = self.storagepools_api.post_storagepools_storagepoolname_filesystems(
            node_id=self.nodeid,
            storagepoolname=self.data['name'])
        self.assertEqual(self.response_filesystem.status_code, 201, " [*] Can't create filesystem on storagepool.")

    def setUp_plus_fileSystem_plus_snapShots(self):
        self.setUp_plus_fileSystem()
        self.lg.info(' [*] Create snapshot (SS0) of filesystem {}'.format(self.data_filesystem['name']))
        self.response_snapshot, self.data_snapshot = self.storagepools_api.post_filesystems_snapshots(self.nodeid,
                                                                                                      self.data['name'],
                                                                                                      self.data_filesystem[
                                                                                                          'name'])
        self.assertEqual(self.response_snapshot.staus_code, 201, " [*] can't create new snapshot.")

    def test001_get_storagepool(self):
        """ GAT-045
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Get storagepool (SP0), should succeed with 200.
        #. Get storagepool (SP0) using python client, should be listed
        #. Get nonexisting storagepool, should fail with 404.
        """
        self.lg.info(' [*] Get storagepool (SP0), should succeed with 200')
        response = self.storagepools_api.get_storagepools_storagepoolname(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        for key in self.data.keys():
            if key == 'devices':
                continue
            self.assertEqual(response.json()[key], self.data[key])

        self.lg.info(' [*] Get storagepool (SP0) using python client, should be listed')
        storagepools = self.core0_client.client.btrfs.list()
        storagepool_sp0 = [x for x in storagepools if x['label'] == 'sp_{}'.format(self.data['name'])]
        self.assertNotEqual(storagepool_sp0, [])
        for device in self.data['devices']:
            self.assertIn(device, [x['path'][:-1] for x in storagepool_sp0[0]['devices']])

        self.lg.info(' [*] Get nonexisting storagepool, should fail with 404')
        response = self.storagepools_api.get_storagepools_storagepoolname(self.nodeid, 'fake_storagepool')
        self.assertEqual(response.status_code, 404)

    def test002_list_storagepool(self):
        """ GAT-046
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. list node (N0) storagepools, storagepool (SP0) should be listed.
        """
        self.lg.info(' [*] list node (N0) storagepools, storagepool (SP0) should be listed')
        response = self.storagepools_api.get_storagepools(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['name'], [x['name'] for x in response.json()])

    def test003_post_storagepool(self):
        """ GAT-047
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create storagepool (SP0) on node (N0).
        #. Get storagepool (SP0), should succeed with 200.
        #. Get storagepool (SP1) using python client, should be listed
        #. Delete Storagepool (SP0), should succeed with 204.
        #. Create invalid storagepool (missing required params), should fail with 400.
        """
        self.lg.info(' [*] Get Storagepool (SP1), should succeed with 200')
        response = self.storagepools_api.get_storagepools_storagepoolname(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        for key in self.data.keys():
            if key == 'devices':
                continue
            self.assertEqual(response.json()[key], self.data[key])

        self.lg.info(' [*] Get storagepool (SP0) using python client, should be listed')
        storagepools = self.core0_client.client.btrfs.list()
        storagepool_sp1 = [x for x in storagepools if x['label'] == 'sp_{}'.format(self.data['name'])]
        self.assertNotEqual(storagepool_sp1, [])

        for device in self.data['devices']:
            self.assertIn(device, [x['path'][:-1] for x in storagepool_sp1[0]['devices']])

        self.lg.info(' [*] Delete Storagepool (SP0), should succeed with 204')
        response = self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Create invalid storagepool, should fail with 400')
        response = self.storagepools_api.post_storagepools(self.nodeid, free_devices=self.freeDisks,
                                                           name='', devices='')
        self.assertEqual(response.status_code, 400)

    def test004_delete_storagepool(self):
        """ GAT-048
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. Delete Storagepool (SP0), should succeed with 204.
        #. list node (N0) storagepools, storagepool (SP0) should be gone.
        #. Delete nonexisting storagepool, should fail with 404.
        """

        self.lg.info(' [*] Delete storagepool (SP0), should succeed with 204')
        response = self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] list node (N0) storagepools, storagepool (SP0) should be gone')
        response = self.storagepools_api.get_storagepools(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['name'], [x['name'] for x in response.json()])

        self.lg.info(' [*] Delete nonexisting storagepool, should fail with 404')
        response = self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, self.rand_str())
        self.assertEqual(response.status_code, 404)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/209')
    def test005_get_storagepool_device(self):
        """ GAT-049
        **Test Scenario:**

        #. Create storagepool (SP0) with device (DV0) on node (N0).
        #. Get device (DV0), should succeed with 200.
        #. Get nonexisting device, should fail with 404.
        """
        self.lg.info(' [*] Get device (DV0), should succeed with 200')
        response = self.storagepools_api.get_storagepools_storagepoolname_devices(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json(), [])
        device_uuid = response.json()[0]['uuid']
        response = self.storagepools_api.get_storagepools_storagepoolname_devices_deviceid(self.nodeid,
                                                                                           self.data['name'],
                                                                                           device_uuid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['deviceName'][:-1], self.data['devices'][0])
        self.assertEqual(response.json()['uuid'], device_uuid)
        self.assertEqual(response.json()['status'], 'healthy')

        self.lg.info(' [*] Get nonexisting device, should fail with 404')
        response = self.storagepools_api.get_storagepools_storagepoolname_devices_deviceid(self.nodeid,
                                                                                           self.data['name'],
                                                                                           self.rand_str())
        self.assertEqual(response.status_code, 404)

    def test006_list_storagepool_devices(self):
        """ GAT-050
        **Test Scenario:**

        #. Create storagepool (SP0) with device (DV0) on node (N0).
        #. list storagepool (SP0) devices, should succeed with 200.
        """
        self.lg.info(' [*] list storagepool (SP0) devices, should succeed with 200')
        response = self.storagepools_api.get_storagepools_storagepoolname_devices(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json(), [])
        self.assertEqual(len(response.json()), len(self.data['devices']))
        self.assertEqual(response.json()[0]['status'], 'healthy')

    def test007_post_storagepool_device(self):
        """ GAT-051
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create storagepool (SP0) with device (DV0) on node (N0).
        #. Create device (DV1) on storagepool (SP0), should succeed with 201.
        #. list storagepool (SP0) devices, device (DV1) should be listed.
        #. Create device with invalid body, should fail with 400.
        """
        self.lg.info(' [*] Create device (DV1) on storagepool (SP0), should succeed with 201')
        free_devices = self.core0_client.getFreeDisks()
        if free_devices == []:
            self.skipTest('no free disks on node {}'.format(self.nodeid))

        device = random.choice(free_devices)
        body = [device]
        response = self.storagepools_api.post_storagepools_storagepoolname_devices(self.nodeid, self.data['name'],
                                                                                   body)
        self.assertEqual(response.status_code, 201)

        for _ in range(30):
            free_devices = self.core0_client.getFreeDisks()
            if device not in free_devices:
                break
            else:
                time.sleep(1)

        self.lg.info(' [*] list storagepool (SP0) devices, should succeed with 200')
        response = self.storagepools_api.get_storagepools_storagepoolname_devices(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(device, [x['deviceName'][:-1] for x in response.json()])

        # issue https://github.com/zero-os/0-orchestrator/issues/398
        # self.lg.info(' [*] Create device with invalid body, should fail with 400')
        # body = ""
        # response = self.storagepools_api.post_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'], body)
        # self.assertEqual(response.status_code, 400)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/209')
    def test008_delete_storagepool_device(self):
        """ GAT-052
        **Test Scenario:**

        #. Create storagepool (SP0) with device (DV0) on node (N1), should succeed with 201.
        #. Delete device (DV0), should succeed with 204.
        #. list storagepool (SP0) devices, device (DV0) should be gone.
        #. Delete nonexisting device, should fail with 404.
        """
        self.lg.info(' [*] Create device (DV1) on storagepool (SP0), should succeed with 201')
        free_devices = self.core0_client.getFreeDisks()
        if free_devices == []:
            self.skipTest('no free disks on node {}'.format(self.nodeid))

        device = random.choice(free_devices)
        body = [device]
        response = self.storagepools_api.post_storagepools_storagepoolname_devices(self.nodeid, self.data['name'],
                                                                                   body)
        self.assertEqual(response.status_code, 201)

        for _ in range(30):
            free_devices = self.core0_client.getFreeDisks()
            if device not in free_devices:
                break
            else:
                time.sleep(1)

        self.lg.info(' [*] list storagepool (SP0) devices, device (DV0) should be gone')
        response = self.storagepools_api.get_storagepools_storagepoolname_devices(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        deviceuuid = [x['uuid'] for x in response.json() if x['deviceName'][:-1] == device]
        self.assertNotEqual(deviceuuid, [], 'device was not added to storagepool')

        self.lg.info(' [*] Delete device (DV1), should succeed with 204')
        response = self.storagepools_api.delete_storagepools_storagepoolname_devices_deviceid(self.nodeid,
                                                                                              self.data['name'],
                                                                                              deviceuuid[0])
        self.assertEqual(response.status_code, 204)

        for _ in range(30):
            free_devices = self.core0_client.getFreeDisks()
            if device in free_devices:
                break
            else:
                time.sleep(1)

        self.lg.info(' [*] list storagepool (SP0) devices, device (DV0) should be gone')
        response = self.storagepools_api.get_storagepools_storagepoolname_devices(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(device, [x['deviceName'][:-1] for x in response.json()])

        self.lg.info(' [*] Delete nonexisting device, should fail with 404')
        response = self.storagepools_api.delete_storagepools_storagepoolname_devices_deviceid(self.nodeid,
                                                                                              self.data['name'],
                                                                                              self.rand_str())
        self.assertEqual(response.status_code, 404)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test009_get_storagepool_filessystem(self):
        """ GAT-053
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Get filesystem (FS0), should succeed with 200.
        #. Get nonexisting filesystem, should fail with 404.
        """
        self.lg.info(' [*] Get filesystem (FS0), should succeed with 200')
        response = self.storagepools_api.get_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid,
                                                                                                     self.data['name'],
                                                                                                     self.data_filesystem[
                                                                                                         'name'])
        self.assertEqual(response.status_code, 200)
        for key in self.data_filesystem.keys():
            self.assertEqual(response.json()[key], self.data_filesystem[key])

        self.lg.info(' [*] Get nonexisting filesystem, should fail with 404')
        response = self.storagepools_api.get_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid,
                                                                                                     self.data['name'],
                                                                                                     self.rand_str())
        self.assertEqual(response.status_code, 404)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test010_list_storagepool_filesystems(self):
        """ GAT-054
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. Create filesystem (FS0) on storagepool (SP0).
        #. list storagepools (SP0) filesystems, filesystem (FS0) should be listed.
        """
        self.lg.info(' [*] list storagepools (SP0) filesystems, filesystem (FS0) should be listed')
        response = self.storagepools_api.get_storagepools_storagepoolname_filesystems(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data_filesystem['name'], response.json())

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test011_post_storagepool_filesystem(self):
        """ GAT-055
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Create storagepool (SP0) on node (N0).
        #. Create filesystem (FS1) on storagepool (SP0), should succeed with 201.
        #. Get filesystem (FS1), should succeed with 200.
        #. Delete filesystem (FS1), should succeed with 204.
        #. Create invalid filesystem (missing required params), should fail with 400.
        """
        self.lg.info(' [*] Get filesystem (FS1), should succeed with 200')
        response = self.storagepools_api.get_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid,
                                                                                                     self.data['name'],
                                                                                                     self.data_filesystem[
                                                                                                         'name'])
        self.assertEqual(response.status_code, 200)
        for key in self.data_filesystem.keys():
            self.assertEqual(response.json()[key], self.data_filesystem[key])

        self.lg.info(' [*] Delete filesystem (FS1), should succeed with 204')
        response = self.storagepools_api.delete_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid,
                                                                                                        self.data[
                                                                                                            'name'],
                                                                                                        self.data_filesystem[
                                                                                                            'name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Create filesystem with invalid body, should fail with 400')
        response = self.storagepools_api.post_storagepools_storagepoolname_filesystems(node_id=self.nodeid,
                                                                                       storagepoolname=self.data[
                                                                                           'name'],
                                                                                       bad_param=self.rand_str())
        self.assertEqual(response.status_code, 400)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test012_delete_storagepool_filesystem(self):
        """ GAT-056
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Delete filesystem (FS0), should succeed with 204.
        #. list storagepool (SP0) filesystems, filesystem (FS0) should be gone.
        #. Delete nonexisting filesystems, should fail with 404.
        """
        self.lg.info(' [*] Delete filesystem (FS0), should succeed with 204')
        response = self.storagepools_api.delete_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid,
                                                                                                        self.data[
                                                                                                            'name'],
                                                                                                        self.data_filesystem[
                                                                                                            'name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] list storagepool (SP0) filesystems, filesystem (FS0) should be gone')
        response = self.storagepools_api.get_storagepools_storagepoolname_filesystems(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data_filesystem['name'], response.json())

        self.lg.info(' [*] Delete nonexisting filesystems, should fail with 404')
        response = self.storagepools_api.delete_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid,
                                                                                                        self.data[
                                                                                                            'name'],
                                                                                                        'fake_filesystem')
        self.assertEqual(response.status_code, 404)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test013_get_storagepool_filessystem_snapshot(self):
        """ GAT-057
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Create snapshot (SS0) on filesystem (FS0).
        #. Get snapshot (SS0), should succeed with 200.
        #. Get nonexisting snapshot, should fail with 404.
        """
        self.lg.info(' [*] Get snapshot (SS0), should succeed with 200')
        response = self.storagepools_api.get_filesystem_snapshots_snapshotname(self.nodeid, self.data['name'],
                                                                               self.data_filesystem['name'],
                                                                               self.data_snapshot['name'])
        self.assertEqual(response.status_code, 200)
        for key in self.data_snapshot.keys():
            self.assertEqual(response.json()[key], self.data_snapshot[key])

        self.lg.info(' [*] Get nonexisting snapshot, should fail with 404')
        response = self.storagepools_api.get_filesystem_snapshots_snapshotname(self.nodeid, self.data['name'],
                                                                               self.data_filesystem['name'],
                                                                               self.rand_str())
        self.assertEqual(response.status_code, 404)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test014_list_storagepool_filesystems_snapshots(self):
        """ GAT-058
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Create snapshot (SS0) on filesystem (FS0).
        #. list snapshots of filesystems (FS0), snapshot (SS0) should be listed.
        """
        self.lg.info(' [*] list snapshots of filesystems (FS0), snapshot (SS0) should be listed')
        response = self.storagepools_api.get_filesystem_snapshots(self.nodeid, self.data['name'],
                                                                  self.data_filesystem['name'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data_snapshot['name'], response.json())

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test015_post_storagepool_filesystem_snapshot(self):
        """ GAT-059
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Create snapshot (SS1) on filesystem (FS0).
        #. Get snapshot (SS1), should succeed with 200.
        #. Delete snapshot (SS1), should succeed with 204.
        #. Create snapshot with missing required params, should fail with 400.
        """
        self.lg.info(' [*]  Get snapshot (SS1), should succeed with 200')
        response = self.storagepools_api.get_filesystem_snapshots_snapshotname(self.nodeid, self.data['name'],
                                                                               self.data_filesystem['name'],
                                                                               self.data_snapshot['name'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], self.data_snapshot['name'])

        self.lg.info(' [*] Delete snapshot (SS1), should succeed with 204')
        response = self.storagepools_api.delete_filesystem_snapshots_snapshotname(self.nodeid, self.data['name'],
                                                                                  self.data_filesystem['name'],
                                                                                  self.data_snapshot['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Create snapshot with missing required params, should fail with 400')
        response = self.storagepools_api.post_filesystems_snapshots(self.nodeid, self.data['name'],
                                                                    self.data_filesystem['name'],
                                                                    name='')
        self.assertEqual(response.status_code, 400)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/658')
    def test016_delete_storagepool_filesystem_snapshot(self):
        """ GAT-060
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Create snapshot (SS0) on filesystem (FS0).
        #. Delete  snapshot (SS0), should succeed with 204.
        #. list filesystem (FS0) snapshots, snapshot (SS0) should be gone.
        #. Delete nonexisting snapshot, should fail with 404.
        """
        self.lg.info(' [*] Delete  snapshot (SS0), should succeed with 204')
        response = self.storagepools_api.delete_filesystem_snapshots_snapshotname(self.nodeid, self.data['name'],
                                                                                  self.data_filesystem['name'],
                                                                                  self.data_snapshot['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] list filesystem (FS0) snapshots, snapshot (SS0) should be gone')
        response = self.storagepools_api.get_filesystem_snapshots(self.nodeid, self.data['name'],
                                                                  self.data_filesystem['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data_snapshot['name'], response.json())

        self.lg.info(' [*] Delete nonexisting snapshot, should fail with 404')
        response = self.storagepools_api.delete_filesystem_snapshots_snapshotname(self.nodeid, self.data['name'],
                                                                                  self.data_filesystem['name'],
                                                                                  'fake_filesystem')
        self.assertEqual(response.status_code, 404)
