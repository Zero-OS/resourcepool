from random import randint
from testcases.testcases_base import TestcasesBase
from nose.tools import with_setup
import time


class TestStorageclustersAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.lg.info(' [*] Deploy new storage cluster (SC0)')
        free_disks = self.core0_client.getFreeDisks()
        if free_disks == []:
            self.skipTest(' [*] No free disks to create storagecluster')
        else:
            self.response, self.data = self.storageclusters_api.post_storageclusters(node_id=self.nodeid,
                                                                                     servers=randint(1, len(free_disks)))
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new storagecluster.")

    def tearDown(self):
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
        self.assertNotEqual(response.json()['status'], 'error')

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
        self.lg.info(' [*] List storage clusters, (SC1) should be listed')
        response = self.storageclusters_api.get_storageclusters()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['label'], response.json())

        self.lg.info(' [*] Kill storage cluster (SC1), should succeed with 204')
        response = self.storageclusters_api.delete_storageclusters_label(self.data['label'])
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
