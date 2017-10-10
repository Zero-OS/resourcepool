from random import randint
from testcases.testcases_base import TestcasesBase
from nose.tools import with_setup
import time


class TestStorageclustersAPI(TestcasesBase):
    def setUp(self):
        super().setUp()

        if self._testID != 'test003_deploy_new_storagecluster':

            nodes = [self.nodeid]
            self.number_of_free_disks, disk_type = self.get_max_available_free_disks(nodes)

            if not number_of_free_disks:
                self.skipTest(' [*] No free disks to create storagecluster')

            self.response, self.data = self.storageclusters_api.post_storageclusters(
                nodes=nodes,
                driveType=disk_type,
                servers=randint(1, self.number_of_free_disks)
            )
            self.assertEqual(self.response.status_code, 201, " [*] Can't create new storagecluster %s." % self.response.content)

    def tearDown(self):
        if self._testID != 'test003_deploy_new_storagecluster':
            self.lg.info(' [*] Kill storage cluster (SC0)')
            self.storageclusters_api.delete_storageclusters_label(self.data['label'])
            super(TestStorageclustersAPI, self).tearDown()

    def test001_get_storageclusters_label(self):
        """ GAT-041
        **Test Scenario:**
        #. Deploy new storage cluster (SC0)
        #. Get storage cluster (SC0), should succeed with 200
        #. Get nonexisting storage cluster (SC0), should fail with 404
        """
        self.lg.info(' [*] Get storage cluster (SC0), should succeed with 200')
        response = self.storageclusters_api.get_storageclusters_label(self.data['label'])
        self.assertEqual(response.status_code, 200)
        for key in ['label', 'driveType', 'nodes']:
            self.assertEqual(response.json()[key], self.data[key])
        self.assertEqual(response.json()['status'], 'ready')

        self.lg.info(' [*] Get nonexisting storage cluster (SC0), should fail with 404')
        response = self.storageclusters_api.get_storageclusters_label(self.rand_str())
        self.assertEqual(response.status_code, 404)

    def test002_list_storageclusters(self):
        """ GAT-042
        **Test Scenario:**
        #. Deploy new storage cluster (SC0)
        #. List storage clusters, should succeed with 200
        """
        self.lg.info(' [*] Get storage cluster (SC0), should succeed with 200')
        response = self.storageclusters_api.get_storageclusters()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['label'], response.json())

    def test003_deploy_new_storagecluster(self):
        """ GAT-043
        **Test Scenario:**
        #. Deploy new storage cluster (SC1), should succeed with 201
        #. List storage clusters, (SC1) should be listed
        #. Kill storage cluster (SC0), should succeed with 204
        """
        nodes = [x['id'] for x in self.nodes_info]
        number_of_free_disks, disk_type = self.get_max_available_free_disks(nodes)

        if not number_of_free_disks:
            self.skipTest('[*] No free disks to create storage cluster')

        if number_of_free_disks < len(nodes):
            servers = number_of_free_disks
            nodes = nodes[:servers]
        else:
            servers = number_of_free_disks - (number_of_free_disks % len(nodes))

        self.lg.info(' [*] Deploy storagecluster with {} servers on {} nodes'.format(servers, len(nodes)))
        response, data = self.storageclusters_api.post_storageclusters(nodes=nodes, driveType=disk_type, servers=servers)
        self.assertEqual(response.status_code, 201)
    
        response = self.storageclusters_api.get_storageclusters_label(data['label'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ready')

        self.lg.info(' [*] Kill storage cluster (SC1), should succeed with 204')
        response = self.storageclusters_api.delete_storageclusters_label(data['label'])
        self.assertEqual(response.status_code, 204)

    def test004_kill_storagecluster_label(self):
        """ GAT-044
        **Test Scenario:**
        #. Kill storage cluster (SC0), should succeed with 204
        #. List storage clusters, (SC0) should be gone
        #. Kill nonexisting storage cluster, should fail with 404
        """
        self.lg.info(' [*] Kill storage cluster (SC0), should succeed with 204')
        response = self.storageclusters_api.delete_storageclusters_label(self.data['label'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List storage clusters, (SC0) should be gone')
        response = self.storageclusters_api.get_storageclusters()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['label'], response.json())

        self.lg.info(' [*] Kill nonexisting storage cluster, should fail with 404')
        response = self.storageclusters_api.delete_storageclusters_label(self.rand_str())
        self.assertEqual(response.status_code, 404)

    def test005_check_disks_wiped(self):
        """ GAT-000
        **Test Scenario:**
        #. Deploy new storage cluster (SC1), should succeed with 201
        #. Check the disks, should be mounted
        #. Kill storage cluster (SC1), should succeed with 204
        #. Make sure the disks are wiped, should succeed
        """

        self.lg.info(' [*] Check the disks, should be mounted')
        #(Pdb) self.data
        #{'label': '8388a225f1', 'servers': 2, 'driveType': 'hdd', 'nodes': ['0cc47a740636'], 'clusterType': 'block'}
        response = self.nodes_api.get_nodes_mounts(self.nodeid)
        s = response.json()
        mounted_disks_num = sum()[1 for x in s if self.data['label'] in x['mountpoint']])
        self.assertEqual(self.data['servers'], mounted_disks_num)

        self.lg.info(' [*] Kill storage cluster (SC1), should succeed with 204')
        response = self.storageclusters_api.delete_storageclusters_label(self.data['label'])
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] Make sure the disks are wiped, should succeed')
        free_disks_num , disk_type = self.get_max_available_free_disks([self.nodeid])
        self.assertEqual(free_disks_num, self.number_of_free_disks)
        mounted_disks_num = sum()[1 for x in s if self.data['label'] in x['mountpoint']])
        self.assertEqual(mounted_disks_num, 0)
