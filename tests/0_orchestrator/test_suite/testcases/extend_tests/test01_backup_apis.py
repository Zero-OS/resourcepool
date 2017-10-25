from random import randint
from testcases.testcases_base import TestcasesBase
import unittest


class TestBackupAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.lg.info('Create new container. ')
        self.created_containers = []
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        self.created_containers.append(self.data['name'])

    def tearDown(self):
        self.lg.info('Delete all created container ')
        for container_name in self.created_containers:
            self.containers_api.delete_containers_containerid(self.nodeid, container_name)

    def test001_list_post_backups(self):
        """ GAT-157

        **Test Scenario:**

        #. Create container C1, should succeed.
        #. Create restic repo, should succeed.
        #. Backup the container (C1) image, should succeed
        #. List the backups and get the backup snapshot, should succeed
        #. Create container with restored data only, and change the nics .. should succeed
        #. Check that the restored files are the same as the original backup.
        """

        self.lg.info('Create restic repo, should succeed')
        self.core0_client.client.bash('echo rooter > /password')
        repo = 'repo' + str(randint(1, 500))
        response = self.core0_client.client.bash('restic init --repo /var/cache/containers/%s --password-file /password'% repo).get()
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info('Backup the container (C1) image, should succeed')
        url = 'file:///var/cache/containers/%s?password=rooter' % repo
        response = self.backup_api.post_container_backups(self.data['name'], url)
        self.assertEqual(response.status_code, 201)

        self.lg.info('List the backups and get the backup snapshot, should succeed')
        response = self.backup_api.list_backups()
        self.assertEqual(response.status_code, 200)
        snapshot = [bkp['snapshot'] for bkp in response.json() if bkp['meta']['name'] == self.data['name']]
        self.assertTrue(snapshot)

        self.lg.info('Create container with restored data only, should succeed')
        res_url = 'restic:' + url + '#{}'.format(snapshot[0])
        self.lg.info(' [*] Create new container. ')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid,
                                                                       flist=res_url)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        self.created_containers.append(self.data['name'])

        self.lg.info('Check that the restored files are the same as the original backup')
        cont_id = int(list(self.core0_client.client.container.find(self.data['name']).keys())[0])
        cont_cl = self.core0_client.client.container.client(cont_id)
        self.assertEqual(cont_cl.filesystem.list("/bin")[0]['name'], 'nbdserver')
