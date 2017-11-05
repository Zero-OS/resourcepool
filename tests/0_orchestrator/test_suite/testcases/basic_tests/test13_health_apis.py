import random, time, unittest
from testcases.testcases_base import TestcasesBase

class TestNodeHealthcheckAPI(TestcasesBase):

    def setUp(self):
        super().setUp()
        self.core0_client.client.timeout = 20
        self.lg.info(' [*] Get healthcheck of random node ')
        response = self.healthcheck_api.get_node_health(nodeid=self.nodeid)
        self.assertEqual(response.status_code, 200)
    
    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1332')
    def test01_get_nodes_healthcheck(self):
        """ GAT-168

        **Test Scenario:**

        #. List all nodes health, should succeed with 200.
        #. Check that all nodes have health check, should succeed.
        """

        self.lg.info("[*] List all nodes health, should succeed with 200")
        response = self.healthcheck_api.get_all_nodes_health()
        self.assertEqual(response.status_code, 200)

        nodes_healthcheck = response.json() 
        nodes_info = [{'id':node['id'], 'status':node['status'], 'hostname':node['hostname']} for node in self.nodes_info]
        self.assertEqual(nodes_healthcheck, nodes_info)

    def test02_get_node_healthcheck(self):
        """ GAT-169

        **Test Scenario:**

        #. Get random node (N0).
        #. Check node (N0) healthchecks, should succeed with 200.
        """
        self.lg.info("Check node (N0) healthchecks, should succeed with 200")
        response = self.healthcheck_api.get_node_health(nodeid=self.nodeid)
        self.assertEqual(response.status_code, 200)

    def test03_disk_usage_checks(self):
        """ GAT-170

        **Test Scenario:**

        #. Get random node (N0).
        #. Choose random free device (DE0) from node (N0) devices.
        #. Create storagepool (SP0) and attach device (DE0) to it, should succeed.
        #. Create filesystem (FS0), should succeed.
        #. Get node (N0) healthchecks, device (DE0) usage status should be (OK).
        #. Write file (F0) with size equal to (91 %) of device (DE0) space.
        #. Get node (N0) healthchecks, device (DE0) usage status should be (WARNING).
        #. Remove file (F0).
        #. Write file (F1) with size equal to (95 %) of device (DE0) space.
        #. Get node (N0) healthchecks, device (DE0) usage status should be (ERROR).
        #. Delete storagepool (SP0), should succeed.
        """
        def get_disk_usage(target_disk):
            if target_disk['type'] == 'nvme':
                targe_disk_name = '{}p1_usage'.format(target_disk['name'])
            else:
                targe_disk_name = '{}1_usage'.format(target_disk['name'])

            response = self.healthcheck_api.get_node_health(nodeid=self.nodeid)
            self.assertEqual(response.status_code, 200)

            healthchecks = response.json()['healthchecks']
            disk_usage = [x for x in healthchecks if x['id'] == 'disk-usage'][0]
            target_disk_usage = [x for x in disk_usage['messages'] if x['id'] == targe_disk_name]
            self.assertNotEqual(target_disk_usage, [])
            return target_disk_usage[0]

        node_free_disks = self.core0_client.getFreeDisks() 
        target_disk = random.choice(node_free_disks)

        self.lg.info('Choose random free device (DE0) from node (N0) devices')
        response, storagepool = self.storagepools_api.post_storagepools(self.nodeid, free_devices=[target_disk['name']])
        self.assertEqual(response.status_code, 201)

        self.lg.info('Create filesystem (FS0), should succeed')
        response, filesystem = self.storagepools_api.post_storagepools_storagepoolname_filesystems(
            self.nodeid, storagepool['name'], quota=0, readOnly=False
        )
        self.assertEqual(response.status_code, 201)

        time.sleep(35)

        self.lg.info('Get node (N0) healthchecks, device (DE0) usage status should be (OK)')
        disk_usage = get_disk_usage(target_disk)
        self.assertEqual(disk_usage['status'], 'OK')

        path = '/mnt/storagepools/{}/filesystems/{}'.format(storagepool['name'], filesystem['name'])
                
        self.lg.info('Write file (F0) with size equal to (91 %) of device (DE0) space')
        filename = self.random_string()
        filesize = int(0.91 * target_disk['size'])
        cmd = 'cd {path}; fallocate -l {filesize}G {filename}'.format(
            path=path,
            filename=filename,
            filesize=filesize
        )
        response = self.core0_client.bash(cmd)
        self.assertEqual(response.state, 'SUCCESS')

        time.sleep(35)

        self.lg.info('Get node (N0) healthchecks, device (DE0) usage status should be (WARNING)')
        disk_usage = get_disk_usage(target_disk)
        self.assertEqual(disk_usage['status'], 'WARNING')

        self.lg.info('Remove file (F0)')
        cmd = 'rm -f {}/*'.format(path)
        self.core0_client.bash(cmd)

        self.lg.info('Write file (F1) with size equal to (95 %) of device (DE0) space')
        filename = self.random_string()
        filesize = int(0.95 * target_disk['size'])
        cmd = 'cd {path}; fallocate -l {filesize}G {filename}'.format(
            path=path,
            filename=filename,
            filesize=filesize
        )
        response = self.core0_client.bash(cmd)
        self.assertEqual(response.state, 'SUCCESS')

        time.sleep(35)

        self.lg.info('Get node (N0) healthchecks, device (DE0) usage status should be (ERROR)')
        disk_usage = get_disk_usage(target_disk)
        self.assertEqual(disk_usage['status'], 'ERROR')

        self.lg.info('Delete storagepool (SP0), should succeed')
        response = self.storagepools_api.delete_storagepools_storagepoolname(self.nodeid, storagepool['name'])
        self.assertEqual(response.status_code, 204)
