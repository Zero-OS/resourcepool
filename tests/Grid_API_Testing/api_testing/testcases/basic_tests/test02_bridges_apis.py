from random import randint
import unittest, time
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.grid_apis.pyclient.bridges_apis import BridgesAPI
from api_testing.python_client.client import Client

class TestBridgesAPI(TestcasesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridges_api = BridgesAPI()

    def setUp(self):
        super(TestBridgesAPI, self).setUp()

        self.lg.info('Get random nodid (N0)')
        self.nodeid = self.get_random_node()
        pyclient_ip = [x['ip'] for x in self.nodes if x['id'] == self.nodeid][0]
        self.pyclient = Client(pyclient_ip)

        self.lg.info('Create bridge (B0) on node (N0)')
        self.name = self.rand_str()
        self.hwaddr = self.randomMAC()
        self.networkMode = "none"
        self.nat = False
        self.settings = {}
        self.body = {"name":self.name,
                	"hwaddr":self.hwaddr,
                	"networkMode":self.networkMode,
                	"nat":self.nat,
                	"setting":self.settings}
        self.bridges_api.post_nodes_bridges(self.nodeid, self.body)
        time.sleep(3)

    def tearDown(self):
        self.lg.info('Delete bridge (B0)')
        self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, self.name)
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
        response = self.bridges_api.get_nodes_bridges_bridgeid(self.nodeid, self.name)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.name, response.json()['name'])
        self.assertEqual('up', response.json()['status'])
        bridges = self.pyclient.client.bridge.list()
        self.assertIn(self.name, bridges)

        self.lg.info('Get nonexisting bridge, should fail with 404')
        response = self.bridges_api.get_nodes_bridges_bridgeid(self.nodeid, 'fake_bridge')
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
        self.assertIn(self.name, [x['name'] for x in response.json()])

    def test003_create_bridge(self):
        """ GAT-020
        *POST:/nodes/{nodeid}/bridges *

        **Test Scenario:**

        #. Get random node (N0).
        #. Create bridge (B1) on node (N0), should succeed with 201.
        #. Get bridges using pyclient , (B1) should be listed
        #. List node (N0) bridges, (B1) should be listed.
        #. Delete bridge (B1), should succeed with 204.
        """
        self.lg.info('Create bridge (B1) on node (N0), should succeed with 201')
        name = self.rand_str()
        hwaddr = self.randomMAC()
        networkMode = self.random_item(["none", "static", "dnsmasq"])
        nat = self.random_item([False, True])
        settings = {"none":{},
                    "static":{"cidr":"192.100.1.0/16"},
                    "dnsmasq":{"cidr":"192.100.2.0/16", "start":"192.100.2.1", "end":"192.100.2.5"}}

        body = {"name":name,
                "hwaddr":hwaddr,
                "networkMode":networkMode,
                "nat":nat,
                "setting":settings[networkMode]}

        response = self.bridges_api.post_nodes_bridges(self.nodeid, body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        bridges = self.pyclient.client.bridge.list()
        self.assertIn(name, bridges)

        nics = self.pyclient.client.info.nic()
        self.assertEqual(hwaddr, [x['hardwareaddr'] for x in nics if x['name'] == name ][0])

        self.lg.info('Get bridge (B0), should succeed with 200')
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(name, [x['name'] for x in response.json()])

        self.lg.info('Delete bridge (B1), should succeed with 204')
        response = self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, name)
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
        response = self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, self.name)
        self.assertEqual(response.status_code, 204)

        bridges = self.pyclient.client.bridge.list()
        self.assertNotIn(self.name, bridges)

        self.lg.info('List node (N0) bridges, (B0) should be gone')
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.name, [x['name'] for x in response.json()])
