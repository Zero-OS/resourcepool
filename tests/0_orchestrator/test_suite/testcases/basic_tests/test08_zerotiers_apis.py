import time
from testcases.testcases_base import TestcasesBase

class TestZerotiersAPI(TestcasesBase):

    @classmethod
    def setUpClass(cls):
        self = cls()
        super(TestZerotiersAPI, self).setUp()
        self.lg.info(' [*] Join zerotier network (ZT0)')
        TestZerotiersAPI.nodeid = self.nodeid
        TestZerotiersAPI.core0_client = self.core0_client
        TestZerotiersAPI.nw_id = self.create_zerotier_network()
        self.response, self.data = self.zerotiers_api.post_nodes_zerotiers(TestZerotiersAPI.nodeid, nwid=TestZerotiersAPI.nw_id)
        
        for i in range(75):
            response = self.zerotiers_api.get_nodes_zerotiers_zerotierid(
                nodeid=TestZerotiersAPI.nodeid, 
                zerotierid=TestZerotiersAPI.nw_id
            )
            self.assertEqual(response.status_code, 200)

            if response.json()['assignedAddresses']:
                break
            else:
                time.sleep(5)
        else:
            self.fail("[*] Can't join zerotier network {}".format(TestZerotiersAPI.nw_id))


    @classmethod
    def tearDownClass(cls):
        self = cls()
        self.lg.info(' [*] Exit zerotier network (ZT0)')
        self.zerotiers_api.delete_nodes_zerotiers_zerotierid(TestZerotiersAPI.nodeid, zerotierid=TestZerotiersAPI.nw_id)
        self.delete_zerotier_network(nwid=TestZerotiersAPI.nw_id)

    def test001_get_nodes_zerotiers_zerotierid(self):
        """ GAT-078
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Join zerotier network (ZT0).
        #. Get zerotier (ZT0) details and compare it with results from python client, should succeed with 200.
        #. Get non-existing zerotier network, should fail with 404.
        """
        self.lg.info(' [*] Get zerotier (ZT0) details and compare it with results from python client, should succeed with 200')
        response = self.zerotiers_api.get_nodes_zerotiers_zerotierid(nodeid=TestZerotiersAPI.nodeid, zerotierid=TestZerotiersAPI.nw_id)
        self.assertEqual(response.status_code, 200)
        core_0_zerotiers = TestZerotiersAPI.core0_client.client.zerotier.list()

        zerotier_ZT0 = [x for x in core_0_zerotiers if x['nwid'] == TestZerotiersAPI.nw_id]
        self.assertNotEqual(zerotier_ZT0, [])

        for key in zerotier_ZT0[0].keys():
            expected_result = zerotier_ZT0[0][key]
            if type(expected_result) == str and key != 'status':
                expected_result = expected_result.lower()
            if key in ['routes', 'id']:
                continue
            self.assertEqual(response.json()[key], expected_result, expected_result)

        self.lg.info(' [*] Get non-existing zerotier network, should fail with 404')
        response = self.zerotiers_api.get_nodes_zerotiers_zerotierid(TestZerotiersAPI.nodeid, self.rand_str())
        self.assertEqual(response.status_code, 404)

    def test002_list_post_node_zerotiers(self):
        """ GAT-079
        **Test Scenario:**

        #. Join zerotier network (ZT0).
        #. Get node (N0) zerotiers networks, should succeed with 200.
        #. List zerotier networks using python client, (ZT0) should be listed
        #. Join zerotier with invalid body, should fail with 400.

        """
        self.lg.info(' [*] Get node (N0) zerotiers networks, should succeed with 200')
        response = self.zerotiers_api.get_nodes_zerotiers(TestZerotiersAPI.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(TestZerotiersAPI.nw_id, [x['nwid'] for x in response.json()])

        self.lg.info(' [*] List zerotier networks using python client, (ZT0) should be listed')
        zerotiers = TestZerotiersAPI.core0_client.client.zerotier.list()
        self.assertIn(TestZerotiersAPI.nw_id, [x['nwid'] for x in zerotiers])

        self.lg.info(' [*] Join zerotier with invalid body, should fail with 400')
        data = {"worngparameter": self.rand_str()}
        response = self.zerotiers_api.post_nodes_zerotiers(TestZerotiersAPI.nodeid, data=data)
        self.assertEqual(response[0].status_code, 400)

    def test003_leave_zerotier(self):
        """ GAT-080
        **Test Scenario:**

        #. Leave zerotier network (ZT0), should succeed with 204.
        #. List node (N0) zerotier networks, (ZT0) should be gone.
        #. List zerotier networks using python client, (ZT0) should be gone.
        #. Leave nonexisting zerotier network, should fail with 404
        """
        self.lg.info(' [*] Leave zerotier network (ZT0), should succeed with 204')
        response = self.zerotiers_api.delete_nodes_zerotiers_zerotierid(TestZerotiersAPI.nodeid, zerotierid=TestZerotiersAPI.nw_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List node (N0) zerotier networks, (ZT0) should be gone')
        response = self.zerotiers_api.get_nodes_zerotiers(TestZerotiersAPI.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(TestZerotiersAPI.nw_id, [x['nwid'] for x in response.json()])

        self.lg.info(' [*] List zerotier networks using python client, (ZT0) should be gone')
        zerotiers = TestZerotiersAPI.core0_client.client.zerotier.list()
        self.assertNotIn(TestZerotiersAPI.nw_id, [x['nwid'] for x in zerotiers])

        self.lg.info(' [*] Leave nonexisting zerotier network, should fail with 404')
        response = self.zerotiers_api.delete_nodes_zerotiers_zerotierid(TestZerotiersAPI.nodeid, zerotierid='fake_zerotier')
        self.assertEqual(response.status_code, 404)
        