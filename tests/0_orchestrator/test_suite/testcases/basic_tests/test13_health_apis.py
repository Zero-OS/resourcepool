import random, time, unittest
from testcases.testcases_base import TestcasesBase

class TestNodeHealthcheckAPI(TestcasesBase):

    def setUp(self):
        super().setUp()
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
        #. Choose random free disk (FD0) from node (N0) disks.
        #. Create btrfs filesystem and Mount disk (FD0).
        #. Write file (F1) with size equal to (91 %) of disk (FD0) space.
        #. Get node (N0) healthchecks, disk (FD0) usage status should be warning.
        #. Remove file (F1).
        #. Write file (F2) with size equal to (95 %) of disk (FD0) space.
        #. Get node (N0) healthchecks, disk (FD0) usage status should be error.
        #. Remove file (F2).
        """

        def get_disk_usage(diskname):
            response = self.healthcheck_api.get_node_health(nodeid=self.nodeid)
            self.assertEqual(response.status_code, 200)

            healthchecks = response.json()['healthchecks']
            disk_usage = [x for x in healthchecks if x['id'] == 'disk-usage'][0]
            target_disk_usage = [x for x in disk_usage['messages'] if x['id'] == '{}_usage'.format(diskname)]
            self.assertNotEqual(target_disk_usage, [])
            return target_disk_usage[0]

        def write_file_to_disk(filesize, path):
            filename = self.random_string()
            cmd = 'cd {path}; fallocate -l {filesize}G {filename}'.format(
                path=path,
                filename=filename,
                filesize=filesize
            )
            response = self.core0_client.bash(cmd)
            self.assertEqual(response.state, 'SUCCESS')
            return filename

        def remove_file_from_disk(path, filename):
            cmd = 'rm -f {}/{}'.format(path, filename)
            response = self.core0_client.bash(cmd)
            self.assertEqual(response.state, 'SUCCESS')


        node_free_disks = self.core0_client.getFreeDisks()
        
        if not node_free_disks:
            self.skipTest('No free disks to preform tests')
        
        self.lg.info('Choose random free disk (FD0) from node (N0) disks ')
        target_disk = random.choice(node_free_disks)
        mountpoint = '/mnt/{}'.format(self.random_string())

        self.lg.info('Create btrfs filesystem and Mount disk (FD0)')
        cmd = 'mkdir {mountpoint}; mkfs.btrfs {target_disk}; mount {target_disk} {mountpoint}'.format(
            target_disk=target_disk['name'],
            mountpoint=mountpoint
        )
        response = self.core0_client.bash(cmd)
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info('Write file (F1) with size equal to (91 %) of disk (FD0) space')
        filesize = int(0.91 * target_disk['size'])
        filename = write_file_to_disk(filesize=filesize, path=mountpoint)

        time.sleep(30)

        self.lg.info('Get node (N0) healthchecks, disk (FD0) usage status should be warning')
        disk_usage = get_disk_usage(target_disk['name'])
        self.assertEqual(disk_usage['status'], 'WARNING')

        self.lg.info('Remove file (F1)')
        remove_file_from_disk(mountpoint, filename)

        self.lg.info('Write file (F2) with size equal to (95 %) of disk (FD0) space')
        filesize = int(0.95 * target_disk['size'])
        filename = write_file_to_disk(filesize=filesize, path=mountpoint)

        time.sleep(30)

        self.lg.info('Get node (N0) healthchecks, disk (FD0) usage status should be error')
        disk_usage = get_disk_usage(target_disk['name'])
        self.assertEqual(disk_usage['status'], 'ERROR')

        self.lg.info('Remove file (F2)')
        remove_file_from_disk(mountpoint, filename)
        self.core0_client.client.bash('umount {}'.format(mountpoint))
        self.core0_client.client.bash('dd if=/dev/zero bs=1M count=500 of={}'.format(target_disk['name']))





 




        





