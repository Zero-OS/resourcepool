import time
from testcases.testcases_base import TestcasesBase


class TestBridgesAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.lg.info('Create bridge (B0) on node (N0)')
        self.response, self.data = self.bridges_api.post_nodes_bridges(node_id=self.nodeid)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new bridge.")
        time.sleep(3)

    def tearDown(self):
        self.lg.info('Delete bridge (B0)')
        self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, self.data['name'])
        super(TestBridgesAPI, self).tearDown()

    def test001_get_bridges_bridgeid(self):
        """ GAT-018
        *GET:/nodes/{nodeid}/bridges/{bridgeid} *

        **Test Scenario:**

        #. Get random node (N0).
        #. Create bridge (B0) on node (N0).
        #. Get bridge (B0), should succeed with 200.
        #. Get nonexisting bridge, should fail with 404.
        """
        self.lg.info('Get bridge (B0), should succeed with 200')
        response = self.bridges_api.get_nodes_bridges_bridgeid(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.data['name'], response.json()['name'])
        self.assertEqual('up', response.json()['status'])

        self.lg.info('Get nonexisting bridge, should fail with 404')
        response = self.bridges_api.get_nodes_bridges_bridgeid(self.nodeid, self.rand_str())
        self.assertEqual(response.status_code, 404)

    def test002_list_node_bridges(self):
        """ GAT-019
        *GET:/nodes/{nodeid}/bridges *

        **Test Scenario:**

        #. Get random node (N0).
        #. Create bridge (B0) on node (N0).
        #. List node (N0) bridges, should succeed with 200.
        """
        self.lg.info('Get bridge (B0), should succeed with 200')
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.data['name'], [x['name'] for x in response.json()])

    def test003_create_bridge(self):
        """ GAT-020
        *POST:/nodes/{nodeid}/bridges *

        **Test Scenario:**

        #. Get random node (N0).
        #. Create bridge (B1) on node (N0), should succeed with 201.
        #. Get bridges using orchestrator_client , (B1) should be listed
        #. List node (N0) bridges, (B1) should be listed.
        #. Delete bridge (B1), should succeed with 204.
        """
        self.lg.info('Create bridge (B1) on node (N0), should succeed with 201')
        response, data = self.bridges_api.post_nodes_bridges(self.nodeid)

        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        bridges = self.core0_client.client.bridge.list()
        self.assertIn(data['name'], bridges)

        nics = self.core0_client.client.info.nic()
        self.assertEqual(data['hwaddr'], [x['hardwareaddr'] for x in nics if x['name'] == data['name']][0])

        self.lg.info('Get bridge (B0), should succeed with 200')
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(data['name'], [x['name'] for x in response.json()])

        self.lg.info('Delete bridge (B1), should succeed with 204')
        response = self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, data['name'])
        self.assertEqual(response.status_code, 204)

    def test004_delete_nodes_brigde_bridgeid(self):
        """ GAT-021
        *Delete:/nodes/{nodeid}/bridges/{bridgeid}*

        **Test Scenario:**

        #. Get random node (N0).
        #. Create bridge (B0) on node (N0).
        #. Delete bridge (B0), should succeed with 204.
        #. List node (N0) bridges, (B0) should be gone.
        """
        self.lg.info('Delete bridge (B0), should succeed with 204')
        response = self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 204)

        bridges = self.core0_client.client.bridge.list()
        self.assertNotIn(self.data['name'], bridges)

        self.lg.info('List node (N0) bridges, (B0) should be gone')
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.data['name'], [x['name'] for x in response.json()])
