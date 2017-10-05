import time
from testcases.testcases_base import TestcasesBase

nw_id = None
nodeid = None


class TestZerotiersAPI(TestcasesBase):
    @classmethod
    def setUpClass(cls):
        self = cls()
        global nw_id
        global nodeid
        super(TestZerotiersAPI, self).setUp()
        self.lg.info(' [*] Join zerotier network (ZT0)')
        nodeid = self.nodeid
        nw_id = self.create_zerotier_network()
        self.response, self.data = self.zerotiers_api.post_nodes_zerotiers(nodeid, nwid=nw_id)

    @classmethod
    def tearDownClass(cls):
        self = cls()
        self.lg.info(' [*] Exit zerotier network (ZT0)')
        self.zerotiers_api.delete_nodes_zerotiers_zerotierid(nodeid, zerotierid=nw_id)
        self.delete_zerotier_network(nwid=nw_id)

    def test001_get_nodes_zerotiers_zerotierid(self):
        """ GAT-078
        **Test Scenario:**

        #. Get random nodid (N0), should succeed.
        #. Join zerotier network (ZT0).
        #. Get zerotier (ZT0) details and compare it with results from python client, should succeed with 200.
        #. Get non-existing zerotier network, should fail with 404.
        """
        self.lg.info(' [*] Get zerotier (ZT0) details and compare it with results from python client, should succeed with 200')
        for i in range(75):
            response = self.zerotiers_api.get_nodes_zerotiers_zerotierid(nodeid, zerotierid=nw_id)
            if response.json()['assignedAddresses'] != []:
                break
            time.sleep(5)
        self.assertEqual(response.status_code, 200)
        zerotiers = self.core0_client.client.zerotier.list()
        zerotier_ZT0 = [x for x in zerotiers if x['nwid'] == nw_id]
        self.assertNotEqual(zerotier_ZT0, [])
        for key in zerotier_ZT0[0].keys():
            expected_result = zerotier_ZT0[0][key]
            if type(expected_result) == str and key != 'status':
                expected_result = expected_result.lower()
            if key in ['routes', 'id']:
                continue
            self.assertEqual(response.json()[key], expected_result, expected_result)

        self.lg.info(' [*] Get non-existing zerotier network, should fail with 404')
        response = self.zerotiers_api.get_nodes_zerotiers_zerotierid(nodeid, self.rand_str())
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
        response = self.zerotiers_api.get_nodes_zerotiers(nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(nw_id, [x['nwid'] for x in response.json()])

        self.lg.info(' [*] List zerotier networks using python client, (ZT0) should be listed')
        zerotiers = self.core0_client.client.zerotier.list()
        self.assertIn(nw_id, [x['nwid'] for x in zerotiers])

        self.lg.info(' [*] Join zerotier with invalid body, should fail with 400')
        data = {"worngparameter": self.rand_str()}
        response = self.zerotiers_api.post_nodes_zerotiers(nodeid, data=data)
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
        response = self.zerotiers_api.delete_nodes_zerotiers_zerotierid(nodeid, zerotierid=nw_id)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List node (N0) zerotier networks, (ZT0) should be gone')
        response = self.zerotiers_api.get_nodes_zerotiers(nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(nw_id, [x['nwid'] for x in response.json()])

        self.lg.info(' [*] List zerotier networks using python client, (ZT0) should be gone')
        zerotiers = self.core0_client.client.zerotier.list()
        self.assertNotIn(nw_id, [x['nwid'] for x in zerotiers])

        self.lg.info(' [*] Leave nonexisting zerotier network, should fail with 404')
        response = self.zerotiers_api.delete_nodes_zerotiers_zerotierid(nodeid, zerotierid='fake_zerotier')
        self.assertEqual(response.status_code, 404)
