import time, unittest
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.orchestrator_api.orchestrator_client.zerotiers_apis import ZerotiersAPI
from api_testing.utiles.core0_client import Client

@unittest.skip(' ')
class TestZerotiersAPI(TestcasesBase):

    def setUp(self):
        super().setUp()
        self.vms_api = VmsAPI()
        self.storageclusters_api = Storageclusters()
        self.vdisks_apis = VDisksAPIs()

        self.lg.info('Get random nodid (N0)')
        self.nodeid = self.get_random_node()
        pyclient_ip = [x['ip'] for x in self.nodes if x['id'] == self.nodeid]
        self.assertNotEqual(pyclient_ip, [])
        self.jwt = self.nodes_api.jwt
        self.pyclient = Client(pyclient_ip[0], password=self.jwt)

        self.lg.info('Join zerotier network (ZT0)')
        self.nwid = self.create_zerotier_network()
        self.body = {"nwid":self.nwid}
        self.zerotier_api.post_nodes_zerotiers(self.nodeid, self.body)

        for _ in range(50):
            response = self.zerotier_api.get_nodes_zerotiers_zerotierid(self.nodeid, self.nwid)
            if response.status_code == 200:
                if response.json()['status'] == 'OK':
                    break
                else:
                    time.sleep(3)
            else:
                self.lg.info('can\'t list node zerotier networks')
        else:
            self.lg.info('can\'t join zerotier network after 150 seconds')
            
        
    def tearDown(self):
        self.lg.info('Exit zerotier network (ZT0)')
        self.zerotier_api.delete_nodes_zerotiers_zerotierid(self.nodeid, self.nwid)
        self.delete_zerotier_network(self.nwid)
        super(TestZerotiersAPI, self).tearDown()

    def test001_get_nodes_zerotiers_zerotierid(self):
        """ GAT-078
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Join zerotier network (ZT0).
        #. Get zerotier (ZT0) details and compare it with results from python client, should succeed with 200.
        #. Get non-existing zerotier network, should fail with 404.
        """
        self.lg.info('Get zerotier (ZT0) details and compare it with results from python client, should succeed with 200')
        response = self.zerotier_api.get_nodes_zerotiers_zerotierid(self.nodeid, self.nwid)
        self.assertEqual(response.status_code, 200)
        zerotiers = self.pyclient.client.zerotier.list()
        zerotier_ZT0 = [x for x in zerotiers if x['nwid'] == self.nwid]
        self.assertNotEqual(zerotier_ZT0, [])
        for key in zerotier_ZT0[0].keys():
            expected_result = zerotier_ZT0[0][key]
            if type(expected_result) == str and key != 'status':
                expected_result = expected_result.lower()
            if key in ['routes', 'id']:
               continue
            self.assertEqual(response.json()[key], expected_result, expected_result)

        self.lg.info('Get non-existing zerotier network, should fail with 404')
        response = self.zerotier_api.get_nodes_zerotiers_zerotierid(self.nodeid, self.rand_str())
        self.assertEqual(response.status_code, 404)


    def test002_list_node_zerotiers(self):
        """ GAT-079
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Join zerotier network (ZT0).
        #. List node (N0) zerotiers networks, should succeed with 200.
        #. List zerotier networks using python client, (ZT0) should be listed
        """
        self.lg.info('Get node (N0) zerotiers networks, should succeed with 200')
        response = self.zerotier_api.get_nodes_zerotiers(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.nwid, [x['nwid'] for x in response.json()])

        self.lg.info('List zerotier networks using python client, (ZT0) should be listed')
        zerotiers = self.pyclient.client.zerotier.list()
        self.assertIn(self.nwid, [x['nwid'] for x in zerotiers])

    def test003_post_zerotier(self):
        """ GAT-080
        **Test Scenario:**

        #. Get random nodid (N0).
        #. Join zerotier network (ZT1).
        #. List node (N0) zerotier networks, (ZT1) should be listed.
        #. List zerotier networks using python client, (ZT1) should be listed
        #. Leave zerotier network (ZT1), should succeed with 204.
        #. Join zerotier with invalid body, should fail with 400.
        """
        self.lg.info('Join zerotier network (ZT1)')
        nwid = self.create_zerotier_network()
        body = {"nwid":nwid}
        response = self.zerotier_api.post_nodes_zerotiers(self.nodeid, body)
        self.assertEqual(response.status_code, 201)
        
        for _ in range(50):
            response = self.zerotier_api.get_nodes_zerotiers_zerotierid(self.nodeid, nwid)
            if response.status_code == 200:
                if response.json()['status'] == 'OK':
                    break
                else:
                    time.sleep(3)
            else:
                self.lg.info('can\'t list node zerotier networks')
        else:
            self.lg.info('can\'t join zerotier network after 150 seconds')

        self.lg.info('List node (N0) zerotier networks, (ZT1) should be listed')
        response = self.zerotier_api.get_nodes_zerotiers(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(nwid, [x['nwid'] for x in response.json()])

        self.lg.info('List zerotier networks using python client, (ZT1) should be listed')
        zerotiers = self.pyclient.client.zerotier.list()
        self.assertIn(nwid, [x['id'] for x in zerotiers])

        self.lg.info('Leave zerotier network (ZT1), should succeed with 204')
        response = self.zerotier_api.delete_nodes_zerotiers_zerotierid(self.nodeid, nwid)
        self.assertEqual(response.status_code, 204)

        self.delete_zerotier_network(nwid)

        self.lg.info('Join zerotier with invalid body, should fail with 400')
        body = {"worngparameter":self.rand_str()}
        response = self.zerotier_api.post_nodes_zerotiers(self.nodeid, body)
        self.assertEqual(response.status_code, 400)

    def test004_leave_zerotier(self):
        """ GAT-081
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Join zerotier network (ZT0).
        #. Leave zerotier network (ZT0), should succeed with 204.
        #. List node (N0) zerotier networks, (ZT0) should be gone.
        #. List zerotier networks using python client, (ZT0) should be gone.
        #. Leave nonexisting zerotier network, should fail with 404
        """
        self.lg.info('Leave zerotier network (ZT0), should succeed with 204')
        response = self.zerotier_api.delete_nodes_zerotiers_zerotierid(self.nodeid, self.nwid)
        self.assertEqual(response.status_code, 204)

        self.lg.info('List node (N0) zerotier networks, (ZT0) should be gone')
        response = self.zerotier_api.get_nodes_zerotiers(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.nwid, [x['nwid'] for x in response.json()])

        self.lg.info('List zerotier networks using python client, (ZT0) should be gone')
        zerotiers = self.pyclient.client.zerotier.list()
        self.assertNotIn(self.nwid, [x['nwid'] for x in zerotiers])

        self.lg.info('Leave nonexisting zerotier network, should fail with 404')
        response = self.zerotier_api.delete_nodes_zerotiers_zerotierid(self.nodeid, 'fake_zerotier')
        self.assertEqual(response.status_code, 404)
