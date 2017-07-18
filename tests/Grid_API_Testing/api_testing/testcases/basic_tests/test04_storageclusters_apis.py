from random import randint
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.orchestrator_api.orchestrator_client.storageclusters_apis import Storageclusters
from api_testing.utiles.core0_client import Client
import unittest, time

# @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/644')
class TestStorageclustersAPI(TestcasesBase):

    def setUp(self):
        super().setUp()
        self.storageclusters_api = Storageclusters()

        self.nodeid = self.get_random_node()
        pyclient_ip = [x['ip'] for x in self.nodes if x['id'] == self.nodeid][0]
        self.jwt = self.nodes_api.jwt
        self.pyclient = Client(pyclient_ip, password=self.jwt)

        if self._testMethodName != 'test003_deploy_new_storagecluster':
            
            self.lg.info('Deploy new storage cluster (SC0)')
            free_disks = self.pyclient.getFreeDisks()
            if free_disks == []:
                self.skipTest('no free disks to create storagecluster')

            self.label = self.rand_str()
            self.servers = randint(1,len(free_disks))
            self.drivetype = 'ssd'

            self.body = {
                    "label": self.label,
                    "servers": self.servers,
                    "driveType": self.drivetype,
                    "clusterType": "storage",
                    "nodes":[self.nodeid]
                }

            response = self.storageclusters_api.post_storageclusters(self.body)
            self.assertEqual(response.status_code, 201)
            
            for _ in range(60):
                response = self.storageclusters_api.get_storageclusters_label(self.label)
                if response.status_code == 200:
                    if response.json()['status'] == 'ready':
                        break
                    else:
                        time.sleep(3)
                else:
                    time.sleep(10)
            else:
                self.lg.error('storagecluster status is not ready after 180 sec')
            

    def tearDown(self):
        self.lg.info('Kill storage cluster (SC0)')
        if self._testMethodName != 'test003_deploy_new_storagecluster':
            self.storageclusters_api.delete_storageclusters_label(self.label)
        super(TestStorageclustersAPI, self).tearDown()

    def test001_get_storageclusters_label(self):
        """ GAT-041
        **Test Scenario:**
        #. Deploy new storage cluster (SC0)
        #. Get storage cluster (SC0), should succeed with 200
        #. Get nonexisting storage cluster (SC0), should fail with 404
        """
        self.lg.info('Get storage cluster (SC0), should succeed with 200')
        response = self.storageclusters_api.get_storageclusters_label(self.label)
        self.assertEqual(response.status_code, 200)
        for key in ['label', 'driveType', 'nodes']:
            self.assertEqual(response.json()[key], self.body[key])
        self.assertNotEqual(response.json()['status'], 'error')

        self.lg.info('Get nonexisting storage cluster (SC0), should fail with 404')
        response = self.storageclusters_api.get_storageclusters_label('fake_label')
        self.assertEqual(response.status_code, 404)

    def test002_list_storageclusters(self):
        """ GAT-042
        **Test Scenario:**
        #. Deploy new storage cluster (SC0)
        #. List storage clusters, should succeed with 200
        """
        self.lg.info('Get storage cluster (SC0), should succeed with 200')
        response = self.storageclusters_api.get_storageclusters()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.label, response.json())

    def test003_deploy_new_storagecluster(self):
        """ GAT-043
        **Test Scenario:**
        #. Deploy new storage cluster (SC1), should succeed with 201
        #. List storage clusters, (SC1) should be listed
        #. Kill storage cluster (SC0), should succeed with 204
        """
        self.lg.info('Deploy new storage cluster (SC1), should succeed with 201')
        
        free_disks = self.pyclient.getFreeDisks()
        if free_disks == []:
            self.skipTest('no free disks to create storagecluster')
        
        label = self.rand_str()
        servers = randint(1, len(free_disks))
        drivetype = 'ssd'
        body = {"label": label,
                "servers": servers,
                "driveType": drivetype,
                "clusterType": "storage",
                "nodes":[self.nodeid]}

        response = self.storageclusters_api.post_storageclusters(body)
        self.assertEqual(response.status_code, 201)

        for _ in range(60):
            response = self.storageclusters_api.get_storageclusters_label(label)
            if response.status_code == 200:
                if response.json()['status'] == 'ready':
                    break
                else:
                    time.sleep(3)
            else:
                time.sleep(10)
        else:
            self.lg.error('storagecluster status is not ready after 180 sec')

        self.lg.info('List storage clusters, (SC1) should be listed')
        response = self.storageclusters_api.get_storageclusters()
        self.assertEqual(response.status_code, 200)
        self.assertIn(label, response.json())

        self.lg.info('Kill storage cluster (SC1), should succeed with 204')
        response = self.storageclusters_api.delete_storageclusters_label(label)
        self.assertEqual(response.status_code, 204)

    def test004_kill_storagecluster_label(self):
        """ GAT-044
        **Test Scenario:**
        #. #. Deploy new storage cluster (SC0)
        #. Kill storage cluster (SC0), should succeed with 204
        #. List storage clusters, (SC0) should be gone
        #. Kill nonexisting storage cluster, should fail with 404
        """
        self.lg.info('Kill storage cluster (SC0), should succeed with 204')
        response = self.storageclusters_api.delete_storageclusters_label(self.label)
        self.assertEqual(response.status_code, 204)

        self.lg.info('List storage clusters, (SC0) should be gone')
        response = self.storageclusters_api.get_storageclusters()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.label, response.json())

        self.lg.info('Kill nonexisting storage cluster, should fail with 404')
        response = self.storageclusters_api.delete_storageclusters_label('fake_label')
        self.assertEqual(response.status_code, 404)
