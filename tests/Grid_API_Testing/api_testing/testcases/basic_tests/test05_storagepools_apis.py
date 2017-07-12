import  random
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.orchestrator_api.orchestrator_client.storagepools_apis import StoragepoolsAPI
from api_testing.utiles.core0_client import Client
import unittest, time


class TestStoragepoolsAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.storagepool_api = StoragepoolsAPI()
        self.nodeid = self.get_random_node()
        self.nodeip = [x['ip'] for x in self.nodes if x['id'] == self.nodeid]
        self.jwt = self.nodes_api.jwt
        self.pyclient = Client(self.nodeip[0], password=self.jwt)
        self.CLEANUP = []

    def tearDown(self):
        for storagepool in self.CLEANUP:
            self.storagepool_api.delete_storagepools_storagepoolname(self.nodeid, storagepool)
        super(TestStoragepoolsAPI, self).tearDown()

    def create_storagepool(self):
        freeDisks = self.pyclient.getFreeDisks()
        if freeDisks == []:
            self.skipTest('no free disks on node {}'.format(self.nodeid))

        self.lg.info('Create storagepool (SP0) on node (N0)')
        name = self.random_string()
        metadata = 'single'
        data = 'single'
        device = random.choice(freeDisks)
        body = {"name":name,
                "metadataProfile":metadata,
                "dataProfile":data,
                "devices":[device]}

        response = self.storagepool_api.post_storagepools(self.nodeid, body)
        self.assertEqual(response.status_code, 201)

        for _ in range(60):
            freeDisks = self.pyclient.getFreeDisks()
            if device not in freeDisks:
                self.CLEANUP.append(name)
                break
            else:
                time.sleep(3)
        else:
            self.lg.error('storagepool {} doesn\'t mount device {}'.format(name, device))
            
        return body

    def delete_storage_pool(self, storagepool):
        response = self.storagepool_api.delete_storagepools_storagepoolname(self.nodeid, storagepool)
        if response.status_code == 204:
            try:
                self.CLEANUP.remove(storagepool)
            except:
                pass
        
    def create_filesystem(self, storagepool):
        self.lg.info('Create filesystem (FS0) on storagepool {}'.format(storagepool))
        name = self.random_string()
        quota = random.randint(0, 10)
        body = {"name":name, "quota":quota}
        response = self.storagepool_api.post_storagepools_storagepoolname_filesystems(self.nodeid, storagepool, body)
        self.assertEqual(response.status_code, 201)
        for _ in range(60):
            try:
                data = self.pyclient.client.btrfs.subvol_list('/mnt/storagepools/{}'.format(storagepool))
                filesystems = [x for x in data if 'filesystems' in x['Path']]
                filesystems = [x['Path'][x['Path'].rfind('/')+1:] for x in filesystems]
                if name in filesystems:
                    break
                else:
                    time.sleep(3)
            except:
                pass
        else:
            self.lg.error('filesystem {} is not created {}'.format(name))
        return body
        
    def create_snapshot(self, storagepool, filesystem):
        self.lg.info('Create snapshot (SS0) of filesystem {}'.format(filesystem))
        name = self.rand_str()
        body = {"name":name}
        self.storagepool_api.post_filesystems_snapshots(self.nodeid, storagepool, filesystem, body)

        for _ in range(60):
            try:
                data = self.pyclient.client.btrfs.subvol_list('/mnt/storagepools/{}'.format(storagepool))
                snapshots = [x for x in data if 'snapshots/{}'.format(filesystem) in x['Path']]
                snapshots = [x['Path'][x['Path'].rfind('/')+1:] for x in snapshots]
                if name in snapshots:
                    break
                else:
                    time.sleep(3)
            except:
                pass
        else:
            self.lg.error('snapshot {} is not created {}'.format(name))

        return body
    

    def test001_get_storagepool(self):
        """ GAT-045
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Get storagepool (SP0), should succeed with 200.
        #. Get storagepool (SP0) using python client, should be listed
        #. Get nonexisting storagepool, should fail with 404.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()
        
        self.lg.info('Get storagepool (SP0), should succeed with 200')
        response = self.storagepool_api.get_storagepools_storagepoolname(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        for key in storagepool.keys():
            if key == 'devices':
                continue
            self.assertEqual(response.json()[key], storagepool[key])

        self.lg.info('Get storagepool (SP0) using python client, should be listed')
        storagepools = self.pyclient.client.btrfs.list()
        storagepool_sp0 = [x for x in storagepools if x['label'] == 'sp_{}'.format(storagepool['name'])]
        self.assertNotEqual(storagepool_sp0, [])
        for device in storagepool['devices']: 
            self.assertIn(device, [x['path'][:-1] for x in storagepool_sp0[0]['devices']])

        self.lg.info('Get nonexisting storagepool, should fail with 404')
        response = self.storagepool_api.get_storagepools_storagepoolname(self.nodeid, 'fake_storagepool')
        self.assertEqual(response.status_code, 404)


    def test002_list_storagepool(self):
        """ GAT-046
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. list node (N0) storagepools, storagepool (SP0) should be listed.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('list node (N0) storagepools, storagepool (SP0) should be listed')
        response = self.storagepool_api.get_storagepools(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(storagepool['name'], [x['name'] for x in response.json()])

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

        self.lg.info('Create Storagepool (SP1), should succeed with 201')
        name = self.random_string()
        free_devices = self.pyclient.getFreeDisks()

        levels = ['raid0', 'raid1', 'raid5', 'raid6', 'raid10', 'dup', 'single']

        if free_devices == []:
            self.skipTest('no free disks on node {}'.format(self.nodeid))

        if len(free_devices) < 6:
            metadata = 'single'
            data = 'single'
            devices = [random.choice(free_devices)]
        else:
            metadata = self.random_item(levels)
            data = self.random_item(levels)
            devices = free_devices[:4]

        body = {"name":name,
                "metadataProfile":metadata,
                "dataProfile":data,
                "devices":devices}

        response = self.storagepool_api.post_storagepools(self.nodeid, body)
        self.assertEqual(response.status_code, 201)
        time.sleep(30)

        self.lg.info('Get Storagepool (SP1), should succeed with 200')
        response = self.storagepool_api.get_storagepools_storagepoolname(self.nodeid, name)
        self.assertEqual(response.status_code, 200)
        for key in body.keys():
            if key == 'devices':
                continue
            self.assertEqual(response.json()[key], body[key])

        time.sleep(20)
        self.lg.info('Get storagepool (SP0) using python client, should be listed')
        storagepools = self.pyclient.client.btrfs.list()
        storagepool_sp1 = [x for x in storagepools if x['label'] == 'sp_{}'.format(name)]
        self.assertNotEqual(storagepool_sp1, [])
        
        for device in devices:
            self.assertIn(device, [x['path'][:-1] for x in storagepool_sp1[0]['devices']])

        self.lg.info('Delete Storagepool (SP0), should succeed with 204')
        response = self.storagepool_api.delete_storagepools_storagepoolname(self.nodeid, name)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Create invalid storagepool, should fail with 400')
        body = {"name":name, "metadataProfile":metadata}
        response = self.storagepool_api.post_storagepools(self.nodeid, body)
        self.assertEqual(response.status_code, 400)

    def test004_delete_storagepool(self):
        """ GAT-048
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. Delete Storagepool (SP0), should succeed with 204.
        #. list node (N0) storagepools, storagepool (SP0) should be gone.
        #. Delete nonexisting storagepool, should fail with 404.
        """

        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Delete storagepool (SP0), should succeed with 204')
        response = self.storagepool_api.delete_storagepools_storagepoolname(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 204)
        self.CLEANUP.remove(storagepool['name'])

        self.lg.info('list node (N0) storagepools, storagepool (SP0) should be gone')
        response = self.storagepool_api.get_storagepools(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(storagepool['name'], [x['name'] for x in response.json()])

        self.lg.info('Delete nonexisting storagepool, should fail with 404')
        response = self.storagepool_api.delete_storagepools_storagepoolname(self.nodeid, 'fake_storagepool')
        self.assertEqual(response.status_code, 404)

    # @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/209')
    def test005_get_storagepool_device(self):
        """ GAT-049
        **Test Scenario:**

        #. Create storagepool (SP0) with device (DV0) on node (N0).
        #. Get device (DV0), should succeed with 200.
        #. Get nonexisting device, should fail with 404.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()
        time.sleep(15)

        self.lg.info('Get device (DV0), should succeed with 200')
        response = self.storagepool_api.get_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json(), [])
        device_uuid = response.json()[0]['uuid']

        response = self.storagepool_api.get_storagepools_storagepoolname_devices_deviceid(self.nodeid, storagepool['name'], device_uuid)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['deviceName'][:-1], storagepool['devices'][0])
        self.assertEqual(response.json()['uuid'], device_uuid)
        self.assertEqual(response.json()['status'], 'healthy')

        self.lg.info('Get nonexisting device, should fail with 404')
        response = self.storagepool_api.get_storagepools_storagepoolname_devices_deviceid(self.nodeid, storagepool['name'], 'fake_device')
        self.assertEqual(response.status_code, 404)

    def test006_list_storagepool_devices(self):
        """ GAT-050
        **Test Scenario:**

        #. Create storagepool (SP0) with device (DV0) on node (N0).
        #. list storagepool (SP0) devices, should succeed with 200.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('list storagepool (SP0) devices, should succeed with 200')
        response = self.storagepool_api.get_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.json(), [])
        self.assertEqual(len(response.json()), len(storagepool['devices']))
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
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create device (DV1) on storagepool (SP0), should succeed with 201')
        free_devices = self.pyclient.getFreeDisks()
        if free_devices == []:
            self.skipTest('no free disks on node {}'.format(self.nodeid))

        device = random.choice(free_devices)
        body = [device]
        response = self.storagepool_api.post_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'], body)
        self.assertEqual(response.status_code, 201)
        
        for _ in range(30):
            free_devices = self.pyclient.getFreeDisks()
            if device not in free_devices:
                break
            else:
                time.sleep(1)
            
        self.lg.info('list storagepool (SP0) devices, should succeed with 200')
        response = self.storagepool_api.get_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(device, [x['deviceName'][:-1] for x in response.json()])

        #issue https://github.com/zero-os/0-orchestrator/issues/398
        # self.lg.info('Create device with invalid body, should fail with 400')
        # body = ""
        # response = self.storagepool_api.post_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'], body)
        # self.assertEqual(response.status_code, 400)
    
    # @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/209')
    def test008_delete_storagepool_device(self):
        """ GAT-052
        **Test Scenario:**

        #. Create storagepool (SP0) with device (DV0) on node (N1), should succeed with 201.
        #. Delete device (DV0), should succeed with 204.
        #. list storagepool (SP0) devices, device (DV0) should be gone.
        #. Delete nonexisting device, should fail with 404.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create device (DV1) on storagepool (SP0), should succeed with 201')
        free_devices = self.pyclient.getFreeDisks()
        if free_devices == []:
            self.skipTest('no free disks on node {}'.format(self.nodeid))

        device = random.choice(free_devices)
        body = [device]
        response = self.storagepool_api.post_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'], body)
        self.assertEqual(response.status_code, 201)
        
        for _ in range(30):
            free_devices = self.pyclient.getFreeDisks()
            if device not in free_devices:
                break
            else:
                time.sleep(1)

        self.lg.info('list storagepool (SP0) devices, device (DV0) should be gone')
        response = self.storagepool_api.get_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        deviceuuid = [x['uuid'] for x in response.json() if x['deviceName'][:-1] == device]
        self.assertNotEqual(deviceuuid, [], 'device was not added to storagepool')

        self.lg.info('Delete device (DV1), should succeed with 204')
        response = self.storagepool_api.delete_storagepools_storagepoolname_devices_deviceid(self.nodeid, storagepool['name'], deviceuuid[0])
        self.assertEqual(response.status_code, 204)

        for _ in range(30):
            free_devices = self.pyclient.getFreeDisks()
            if device in free_devices:
                break
            else:
                time.sleep(1)

        self.lg.info('list storagepool (SP0) devices, device (DV0) should be gone')
        response = self.storagepool_api.get_storagepools_storagepoolname_devices(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(device, [x['deviceName'][:-1] for x in response.json()])

        self.lg.info('Delete nonexisting device, should fail with 404')
        response = self.storagepool_api.delete_storagepools_storagepoolname_devices_deviceid(self.nodeid, storagepool['name'], 'fake_device')
        self.assertEqual(response.status_code, 404)

    def test009_get_storagepool_filessystem(self):
        """ GAT-053
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Get filesystem (FS0), should succeed with 200.
        #. Get nonexisting filesystem, should fail with 404.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create filesystem (FS0) on storagepool (SP0)')
        filesystem = self.create_filesystem(storagepool['name'])

        self.lg.info('Get filesystem (FS0), should succeed with 200')
        response = self.storagepool_api.get_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid, storagepool['name'], filesystem['name'])
        self.assertEqual(response.status_code, 200)
        for key in filesystem.keys():
            self.assertEqual(response.json()[key], filesystem[key])

        self.lg.info('Get nonexisting filesystem, should fail with 404')
        response = self.storagepool_api.get_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid, storagepool['name'], 'fake_filesystem')
        self.assertEqual(response.status_code, 404)

    def test010_list_storagepool_filesystems(self):
        """ GAT-054
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. Create filesystem (FS0) on storagepool (SP0).
        #. list storagepools (SP0) filesystems, filesystem (FS0) should be listed.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create filesystem (FS0) on storagepool (SP0)')
        filesystem = self.create_filesystem(storagepool['name'])

        self.lg.info('list storagepools (SP0) filesystems, filesystem (FS0) should be listed')
        response = self.storagepool_api.get_storagepools_storagepoolname_filesystems(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(filesystem['name'], response.json())

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
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()
        
        self.lg.info('Create filesystem (FS1) on storagepool (SP0), should succeed with 201')
        name = self.random_string()
        quota = random.randint(0, 10)
        body = {"name":name, "quota":quota}
        response = self.storagepool_api.post_storagepools_storagepoolname_filesystems(self.nodeid, storagepool['name'], body)
        self.assertEqual(response.status_code, 201)
        time.sleep(5)

        self.lg.info('Get filesystem (FS1), should succeed with 200')
        response = self.storagepool_api.get_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid, storagepool['name'], name)
        self.assertEqual(response.status_code, 200)
        for key in body.keys():
            self.assertEqual(response.json()[key], body[key])

        self.lg.info('Delete filesystem (FS1), should succeed with 204')
        response = self.storagepool_api.delete_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid, storagepool['name'], name)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Create filesystem with invalid body, should fail with 400')
        body = {self.random_string() : self.random_string()}
        response = self.storagepool_api.post_storagepools_storagepoolname_filesystems(self.nodeid, storagepool['name'], body)
        self.assertEqual(response.status_code, 400)

    def test012_delete_storagepool_filesystem(self):
        """ GAT-056
        **Test Scenario:**

        #. Create Storagepool (SP0) on node (N0).
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Delete filesystem (FS0), should succeed with 204.
        #. list storagepool (SP0) filesystems, filesystem (FS0) should be gone.
        #. Delete nonexisting filesystems, should fail with 404.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create filesystem (FS0) on storagepool (SP0)')
        filesystem = self.create_filesystem(storagepool['name'])

        self.lg.info('Delete filesystem (FS0), should succeed with 204')
        response = self.storagepool_api.delete_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid, storagepool['name'], filesystem['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('list storagepool (SP0) filesystems, filesystem (FS0) should be gone')
        response = self.storagepool_api.get_storagepools_storagepoolname_filesystems(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(filesystem['name'], response.json())

        self.lg.info('Delete nonexisting filesystems, should fail with 404')
        response = self.storagepool_api.delete_storagepools_storagepoolname_filesystems_filesystemname(self.nodeid, storagepool['name'], 'fake_filesystem')
        self.assertEqual(response.status_code, 404)

    # @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/687')
    def test013_get_storagepool_filessystem_snapshot(self):
        """ GAT-057
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Create snapshot (SS0) on filesystem (FS0).
        #. Get snapshot (SS0), should succeed with 200.
        #. Get nonexisting snapshot, should fail with 404.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create filesystem (FS0) on storagepool (SP0)')
        filesystem = self.create_filesystem(storagepool['name'])

        self.lg.info('Create snapshot (SS0) on filesystem (FS0)')
        snapshot = self.create_snapshot(storagepool['name'], filesystem['name'])


        self.lg.info('Get snapshot (SS0), should succeed with 200')
        response = self.storagepool_api.get_filesystem_snapshots_snapshotname(self.nodeid, storagepool['name'],
                                                                                           filesystem['name'],
                                                                                           snapshot['name'])
        self.assertEqual(response.status_code, 200)
        for key in snapshot.keys():
            self.assertEqual(response.json()[key], snapshot[key])

        self.lg.info('Get nonexisting snapshot, should fail with 404')
        response = self.storagepool_api.get_filesystem_snapshots_snapshotname(self.nodeid, storagepool['name'],
                                                                                           filesystem['name'],
                                                                                           'fake_snapshot')
        self.assertEqual(response.status_code, 404)

    # @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/687')
    def test014_list_storagepool_filesystems_snapshots(self):
        """ GAT-058
        **Test Scenario:**

        #. Create storagepool (SP0) on node (N0), should succeed.
        #. Create filesystem (FS0) on storagepool (SP0).
        #. Create snapshot (SS0) on filesystem (FS0).
        #. list snapshots of filesystems (FS0), snapshot (SS0) should be listed.
        """
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create filesystem (FS0) on storagepool (SP0)')
        filesystem = self.create_filesystem(storagepool['name'])

        self.lg.info('Create snapshot (SS0) on filesystem (FS0)')
        snapshot = self.create_snapshot(storagepool['name'], filesystem['name'])
        
        self.lg.info('list snapshots of filesystems (FS0), snapshot (SS0) should be listed')
        response = self.storagepool_api.get_filesystem_snapshots(self.nodeid, storagepool['name'], filesystem['name'])
        self.assertEqual(response.status_code, 200)
        self.assertIn(snapshot['name'], response.json())

    # @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/687')
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
        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create filesystem (FS0) on storagepool (SP0)')
        filesystem = self.create_filesystem(storagepool['name'])

        self.lg.info('Create snapshot (SS1) on filesystem (FS0)')
        name = self.random_string()
        body = {"name":name}
        response = self.storagepool_api.post_filesystems_snapshots(self.nodeid, storagepool['name'], filesystem['name'], body)
        self.assertEqual(response.status_code, 201)

        self.lg.info(' Get snapshot (SS1), should succeed with 200')
        response = self.storagepool_api.get_filesystem_snapshots_snapshotname(self.nodeid, storagepool['name'],
                                                                                           filesystem['name'],
                                                                                           name)
        self.assertEqual(response.status_code, 200)
        for key in body.keys():
            self.assertEqual(response.json()[key], body[key])

        self.lg.info('Delete snapshot (SS1), should succeed with 204')
        response = self.storagepool_api.delete_filesystem_snapshots_snapshotname(self.nodeid, storagepool['name'],
                                                                                              filesystem['name'],
                                                                                              name)
        self.assertEqual(response.status_code, 204)

        self.lg.info('Create snapshot with missing required params, should fail with 400')
        body = {}
        response = self.storagepool_api.post_filesystems_snapshots(self.nodeid, storagepool['name'], filesystem['name'], body)
        self.assertEqual(response.status_code, 400)

    # @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/687')
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

        self.lg.info('Create storagepool (SP0) on node (N0), should succeed')
        storagepool = self.create_storagepool()

        self.lg.info('Create filesystem (FS0) on storagepool (SP0)')
        filesystem = self.create_filesystem(storagepool['name'])

        self.lg.info('Create snapshot (SS0) on filesystem (FS0)')
        snapshot = self.create_snapshot(storagepool['name'], filesystem['name'])

        self.lg.info('Delete  snapshot (SS0), should succeed with 204')
        response = self.storagepool_api.delete_filesystem_snapshots_snapshotname(self.nodeid, storagepool['name'],
                                                                                              filesystem['name'],
                                                                                              snapshot['name'])
        self.assertEqual(response.status_code, 204)

        self.lg.info('list filesystem (FS0) snapshots, snapshot (SS0) should be gone')
        response = self.storagepool_api.get_filesystem_snapshots(self.nodeid, storagepool['name'], filesystem['name'])
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(snapshot['name'], response.json())

        self.lg.info('Delete nonexisting snapshot, should fail with 404')
        response = self.storagepool_api.delete_filesystem_snapshots_snapshotname(self.nodeid, storagepool['name'], filesystem['name'], 'fake_filesystem')
        self.assertEqual(response.status_code, 404)
