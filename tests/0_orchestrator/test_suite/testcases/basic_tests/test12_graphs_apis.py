import time, unittest
from testcases.testcases_base import TestcasesBase


class TestGraphsAPI(TestcasesBase):
    def setUp(self):
        super().setUp()

        response = self.graphs_api.get_graphs()

        if not response.json():
            self.skipTest('Can\'t find graph service')
        
        self.graphid = response.json()[-1]['id']

        self.lg.info('Create dashboard')
        response, self.dashboard_data = self.graphs_api.post_dashboard(self.graphid)
        self.assertEqual(response.status_code, 201)

    def tearDown(self):
        self.graphs_api.delete_dashboard_dashboardname(self.graphid, self.dashboard_data['name'])
        super(TestGraphsAPI, self).tearDown()

    def test001_list_graphs(self):
        """ GAT-159
        *GET:/graphs*

        **Test Scenario:**

        #. List graphs, should succeed with 200.
        """
        self.lg.info('List graphs, should succeed with 200')
        response = self.graphs_api.get_graphs()
        self.assertEqual(response.status_code, 200, response.content)

    def test002_get_graph_graphid(self):
        """ GAT-160
        *GET:/graphs/{graphid}*

        **Test Scenario:**

        #. Get graph (G0) info, should succeed with 200.
        #. Get non-existing graph, should fail with 404.
        """
        self.lg.info('Get graph (G0) info, should succeed with 200')
        response = self.graphs_api.get_graphs_graphid(self.graphid)
        self.assertEqual(response.status_code, 200, response.content)

        self.lg.info('Get non-existing graph, should fail with 404')
        response = self.graphs_api.get_graphs_graphid('fake_graphid')
        self.assertEqual(response.status_code, 404, response.content)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1314')
    def test003_put_graph_graphid(self):
        """ GAT-161
        *PUT:/graphs/{graphid}*

        **Test Scenario:**

        #. Update graph (G0) info, should succeed with 204.
        #. Get graph (G0) info, should succeed with 200.
        #. Check that graph (G0) info is updated, should succeed.
        #. Update graph info with invalid body, should fail with 400.
        #. Update non-existing graph, should fail with 404.
        """
        self.lg.info('Update graph (G0) info, should succeed with 204')
        body = {'url':'http://newurl.com'}
        response = self.graphs_api.put_graphs_graphid(graphid=self.graphid, **body)
        self.assertEqual(response.status_code, 204, response.content)

        self.lg.info('Get graph by id, should succeed with 200')
        response = self.graphs_api.get_graphs_graphid(graphid=self.graphid)
        self.assertEqual(response.status_code, 200, response.content)

        self.lg.info('Check that graph (G0) info is updated, should succeed')
        self.assertEqual(response.json()['url'], body['url'])

        self.lg.info('Update graph info with invalid body, should fail with 400')
        body = {'id':123456, 'url':123456} 
        response, data = self.graphs_api.put_graphs_graphid(graphid=self.graphid, **body)
        self.assertEqual(response.status_code, 400, response.content)

        self.lg.info('Update non-existing graph, should fail with 404')
        response, data = self.graphs_api.put_graphs_graphid(graphid='fake_graphid')
        self.assertEqual(response.status_code, 404, response.content)

    def test004_list_graph_dashboards(self):
        """ GAT-162
        *PUT:/graphs/{graphid}/dashboards*

        **Test Scenario:**

        #. Create dashboard (DB0), should succeed with 201.
        #. List dashboards. dashboard (DB0) should be listed.
        """
        self.lg.info('List dashboards. dashboard (DB0) should be listed')
        response = self.graphs_api.get_dashboards(self.graphid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.dashboard_data['name'], [x['name'] for x in response.json()])

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1310')
    def test005_get_graph_dashboard_dashboardname(self):
        """ GAT-163
        *PUT:/graphs/{graphid}/dashboards/{dashboardname}*

        **Test Scenario:**

        #. Create dashboard (DB0), should succeed with 201.
        #. Get dashboard (DB0) info, should succeed with 200.
        """
        self.lg.info('Get dashboard (DB0) info, should succeed with 200')
        response = self.graphs_api.get_dashboard_dashboardname(self.graphid, self.dashboard_data['name'])
        self.assertEqual(response.status_code, 200)

        for key in self.dashboard_data:
            self.assertEqual(response.json()[key], self.dashboard_data[key])
    
    def test006_post_graph_dashboard(self):
        """ GAT-164
        *POST:/graphs/{graphid}/dashboards*

        **Test Scenario:**
        #. Create dashboard (DB0), should succeed with 201.
        #. Create dashboard with the same name of dashboard (DB0), should fail with 409.
        #. Create dashboard with invalid body, should fail with 400.
        """
        self.lg.info('Create dashboard with the same name of dashboard (DB0), should fail with 409')
        response, data = self.graphs_api.post_dashboard(graphid=self.graphid, name=self.dashboard_data['name'])
        self.assertEqual(response.status_code, 409)

        self.lg.info('Create dashboard with invalid body, should fail with 400')
        response, data = self.graphs_api.post_dashboard(graphid=self.graphid, name='')
        self.assertEqual(response.status_code, 400)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1311')
    def test007_delete_graph_dashboard_dashboardname(self):
        """ GAT-165
        *DELETE:/graphs/{graphid}/dashboards/{dashboardname}*

        **Test Scenario:**

        #. Create dashboard (DB0), should succeed.
        #. Delete dashboard (DB0), should scucceed with 204.
        #. List dashboards, Dashboard (DB0) should be gone.
        #. Delete non-existing dashboard, should scucceed with 204.
        """
        self.lg.info('Delete dashboard (DB0), should scucceed with 204')
        response = self.graphs_api.delete_dashboard_dashboardname(self.graphid, self.dashboard_data['name'])
        self.assertEqual(response.status_code, 204, response.content)

        self.lg.info('List graph dashboards, Dashboard (DB0) should be gone')
        response = self.graphs_api.get_dashboards(self.graphid)
        self.assertEqual(response.status_code, 200)
        self.assertNoIn(self.dashboard_data['name'], [x['name'] for x in response.json()])

        self.lg.info('Delete non-existing dashboard, should succeed with 204')
        response = self.graphs_api.delete_dashboard_dashboardname(self.graphid, 'fake_dashboard_name')
        self.assertEqual(response.status_code, 204, response.content)
