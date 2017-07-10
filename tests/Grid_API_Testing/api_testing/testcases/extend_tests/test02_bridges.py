from random import randint
import unittest, time
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.grid_apis.pyclient.bridges_apis import BridgesAPI
from api_testing.grid_apis.pyclient.containers_apis import ContainersAPI
from api_testing.grid_apis.pyclient.nodes_apis import NodesAPI
from api_testing.python_client.core0_client import Client


class TestBridgesAPI(TestcasesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridges_api = BridgesAPI()
        self.containers_api = ContainersAPI()
        self.nodes_api = NodesAPI()
        self.createdbridges = []

    def setUp(self):
        super(TestBridgesAPI, self).setUp()

        self.lg.info('Get random nodid (N0)')
        self.nodeid = self.get_random_node()
        zeroCore_ip = [x['ip'] for x in self.nodes if x['id'] == self.nodeid][0]
        self.root_url = "https://hub.gig.tech/gig-official-apps/ubuntu1604.flist"
        self.zeroCore = Client(zeroCore_ip, password=self.jwt)
        self.bridge_name = self.rand_str()
        self.nat = self.random_item([False, True])
        self.bridge_body = {"name":self.bridge_name,
                            "networkMode": "none",
                            "nat": self.nat,
                            "setting": {}
                            }

    def tearDown(self):
        self.lg.info('TearDown:delete all created bridges ')
        for bridge in self.createdbridges:
            self.bridges_api.delete_nodes_bridges_bridgeid(bridge['node'],
                                                           bridge['name'])

    def test001_create_bridges_with_same_name(self):
        """ GAT-101
        *Create two bridges with same name *

        **Test Scenario:**

        #. Create bridge (B1) , should succeed .
        #. Check that created bridge exist in bridges list.
        #. Create bridge (B2) with same name for (B1),should fail.
        #. Delete bridge (B1), should succeed.

        """
        self.lg.info('Create bridge (B1) , should succeed .')
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        self.lg.info("Check that created bridge exist in bridges list.")
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertTrue([x for x in response.json() if x["name"] == self.bridge_name])

        self.lg.info('Create bridge (B2) with same name for (B1),should fail.')
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.assertEqual(response.status_code, 409, response.content)
        time.sleep(3)

        self.lg.info('Delete bridge (B1), should succeed..')
        response = self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, self.bridge_name)
        self.assertEqual(response.status_code, 204, response.content)

    def test002_create_bridge_with_nat(self):
        """ GAT-102
        *Create bridge with nat options *

        **Test Scenario:**

        #. Create bridge (B0) with false in nat option,should succeed.
        #. Create container (C0) with (B0) bridge,should succeed.
        #. Check that C0 can connect to internet ,should fail.
        #. Create bridge (B1) with true in nat option , should succed.
        #. Create container(C1) with (B1) bridge ,should succeed.
        #. Check that (C1) can connect to internet ,should succeed.

        """
        nat_options = [False, True]
        for i, nat in enumerate(nat_options):
            B_name = self.rand_str()
            cidr = "217.102.2.1"
            B_body = {"name": B_name,
                      "hwaddr": self.randomMAC(),
                      "networkMode": "dnsmasq",
                      "nat": nat,
                      "setting": {"cidr": "%s/24"%cidr,
                      "start": "217.102.2.2",
                      "end": "217.102.2.3"}
                       }

            self.lg.info('Create bridge (B{0}) with dnsmasq and {1} in nat option,should succeed.'.format(i, nat))
            response = self.bridges_api.post_nodes_bridges(self.nodeid, B_body)
            self.assertEqual(response.status_code, 201, response.content)
            time.sleep(3)

            self.lg.info('Create (C{0}) with (B{0}) bridge,should succeed.'.format(i))
            C_nics = [{"type": "bridge", "id": B_name, "config": {"dhcp":True}, "status": "up" }]
            C_name = self.rand_str()
            C_body = {"name": C_name , "hostname":self.rand_str(), "flist": self.root_url,
                   "hostNetworking": False,"nics":C_nics
                      }
            response = self.containers_api.post_containers(self.nodeid, C_body)
            self.assertEqual(response.status_code, 201)
            C_client = self.zeroCore.get_container_client(C_name)
            time.sleep(4)
            if not nat:
                self.lg.info('Check that C{} can connect to internet ,should fail.'.format(i))
                response = C_client.bash("ping -c1 8.8.8.8").get()
                self.assertEqual(response.state, "ERROR", response.stdout)
            else:

                self.lg.info('Check that C{} can connect to internet ,should succeed.'.format(i))
                response = C_client.bash("ping -c1 8.8.8.8").get()
                self.assertEqual(response.state, "SUCCESS", response.stdout)

            self.lg.info('Delete created bridge (B{0}) and container (c{0}), should succeed'.format(i))
            response = self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, B_name)
            self.assertEqual(response.status_code, 204)
            response = self.containers_api.delete_containers_containerid(self.nodeid,
                                                                         C_name)
            self.assertTrue(response.status_code, 204)

    def test003_create_bridge_with_hwaddr(self):
        """ GAT-103
        *Create bridge with hardware address *

        **Test Scenario:**

        #. Create bridge (B0) with specefic hardware address,should succeed.
        #. Check that bridge created with this hardware address, should succeed.
        #. Create bridge (B1) with wrong hardware address, should fail.

        """
        hardwareaddr = self.randomMAC()
        self.bridge_body["hwaddr"] = hardwareaddr
        self.lg.info("Create bridge (B0) with specefic hardware address,should succeed.")
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)
        self.createdbridges.append({"node": self.nodeid, "name": self.bridge_name})

        self.lg.info(" Check that bridge(B0) created with this hardware address, should succeed.")
        response = self.nodes_api.get_nodes_nodeid_nics(self.nodeid)
        self.assertEqual(response.status_code, 200)
        nic = [x for x in response.json() if x["name"] == self.bridge_name][0]
        self.assertEqual(nic["hardwareaddr"], hardwareaddr)

        self.lg.info("Create bridge (B1) with wrong hardware address, should fail.")
        hardwareaddr = self.rand_str()
        B1_name = self.rand_str()
        self.bridge_body["hwaddr"] = hardwareaddr
        self.bridge_body["name"] = B1_name
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": self.bridge_name})
        self.assertEqual(response.status_code, 400, response.content)

    def test004_create_bridge_with_static_networkMode(self):
        """ GAT-104
        *Create bridge with static network mode *

        **Test Scenario:**

        #. Create bridge (B0), should succeed.
        #. Check that (B0)bridge took given cidr address, should succeed.

        """
        cidr_address = "130.111.3.1/8"
        self.bridge_body["networkMode"] = "static"
        self.bridge_body["setting"] = {"cidr": cidr_address}

        self.lg.info(" Create bridge (B0), should succeed.")
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)
        self.createdbridges.append({"node": self.nodeid, "name": self.bridge_name})

        self.lg.info("Check that (B0)bridge took given cidr address, should succeed.")
        response = self.nodes_api.get_nodes_nodeid_nics(self.nodeid)
        self.assertEqual(response.status_code, 200)
        nic = [x for x in response.json() if x["name"] == self.bridge_name][0]
        self.assertIn(cidr_address, nic["addrs"])

    def test005_create_bridges_with_static_networkMode_and_same_cidr(self):
        """ GAT-105
        *Create two bridges with static network mode and same cidr address *

        **Test Scenario:**

        #. Create bridge (B0), should succeed.
        #. Check that created bridge exist in bridges list.
        #. Create bridge(B1)with same cidr as (B0),should fail.

        """

        cidr_address = "130.111.3.1/8"
        self.bridge_body["networkMode"] = "static"
        self.bridge_body["setting"] = {"cidr": cidr_address}

        self.lg.info(" Create bridge (B0), should succeed.")
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)
        self.createdbridges.append({"node": self.nodeid, "name": self.bridge_name})

        self.lg.info("Check that created bridge exist in bridges list.")
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertTrue([x for x in response.json() if x["name"] == self.bridge_name])

        self.lg.info("Create bridge(B1)with same cidr as (B0),should fail.")
        B1_name = self.rand_str()
        self.bridge_body["name"] = B1_name
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": B1_name})
        self.assertEqual(response.status_code, 409, response.content)

    def test006_create_bridge_with_invalid_cidr_in_static_networkMode(self):
        """ GAT-106
        *Create bridge with static network mode and invalid cidr address  *

        **Test Scenario:**

        #. Create bridge (B) with invalid cidr address, should fail.

        """

        self.lg.info(" Create bridge (B) with invalid cidr address, should fail..")
        B_name = self.rand_str()
        cidr_address = "260.120.3.1/8"
        self.bridge_body["name"] = B_name
        self.bridge_body["networkMode"] = "static"
        self.bridge_body["setting"] = {"cidr": cidr_address}
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": B_name})
        self.assertEqual(response.status_code, 400, response.content)

    def test007_create_bridge_with_empty_setting_in_static_networkMode(self):
        """ GAT-107
        *Create bridge with static network mode and invalid empty cidr address. *

        **Test Scenario:**

        #. Create bridge (B) with static network mode and empty cidr value,should fail.

        """

        self.lg.info(" Create bridge (B) with static network mode and empty cidr value,should fail.")
        B_name = self.rand_str()
        self.bridge_body["name"] = B_name
        self.bridge_body["networkMode"] = "static"
        self.bridge_body["setting"] = {}
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": B_name})
        self.assertEqual(response.status_code, 400, response.content)

    def test008_create_bridge_with_dnsmasq_networkMode(self):
        """ GAT-108
        *Create bridge with dnsmasq network mode *

        **Test Scenario:**

        #. Create bridge (B) with dnsmasq network mode, should succeed.
        #. Check that (B)bridge took given cidr address, should succeed.

        """

        cidr_address = "205.102.2.1/8"
        start = "205.102.3.2"
        end = "205.102.3.3"
        self.bridge_body["networkMode"] = "dnsmasq"
        self.bridge_body["setting"] = {"cidr": cidr_address, "start": start, "end": end}

        self.lg.info(" Create bridge (B) with dnsmasq network mode,cidr value and start and end range in settings, should succeed.")
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)
        self.createdbridges.append({"node": self.nodeid, "name": self.bridge_name})

        self.lg.info("Check that (B) bridge took given cidr address, should succeed.")
        response = self.nodes_api.get_nodes_nodeid_nics(self.nodeid)
        self.assertEqual(response.status_code, 200)
        nic = [x for x in response.json() if x["name"] == self.bridge_name][0]
        self.assertIn(cidr_address, nic["addrs"])



    def test009_create_bridges_with_dnsmasq_networkMode_and_opverlapping_cidrs(self):
        """ GAT-109
        *Create bridges with dnsmasq network mode and overlapping cidrs. *

        **Test Scenario:**

        #. Create bridge (B0) with dnsmasq network mode, should succeed.
        #. Check that created bridge exist in bridges list.
        #. Create bridge (B1) overlapping with (B0) cidr address,shoud fail.

        """

        cidr_address = "205.102.2.1/8"
        start = "205.102.3.2"
        end = "205.102.3.3"
        self.bridge_body["networkMode"] = "dnsmasq"
        self.bridge_body["setting"] = {"cidr": cidr_address, "start": start, "end": end}

        self.lg.info(" Create bridge (B0) with dnsmasq network mode,cidr value and start and end range in settings, should succeed.")
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)
        self.createdbridges.append({"node": self.nodeid, "name": self.bridge_name})

        self.lg.info("Check that created bridge exist in bridges list.")
        response = self.bridges_api.get_nodes_bridges(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertTrue([x for x in response.json() if x["name"] == self.bridge_name])

        self.lg.info(" Create bridge (B1) overlapping with (B0) address,shoud fail.")
        B1_name = self.rand_str()
        cidr_address = "205.103.2.1/8"
        start = "205.103.3.2"
        end = "205.103.3.2"
        self.bridge_body["name"] = B1_name
        self.bridge_body["networkMode"] = "dnsmasq"
        self.bridge_body["setting"] = {"cidr": cidr_address, "start": start, "end": end}
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": B1_name})
        self.assertEqual(response.status_code, 409, response.content)

    def test010_create_bridge_with_out_of_range_address_in_dnsmasq(self):
        """ GAT-110
        *Create bridge with dnsmasq network mode and out of range start and end values *

        **Test Scenario:**

        #. Create bridge(B) with out of range start and end values, shoud fail.

        """

        self.lg.info("Create bridge(B) with out of range start and end values, shoud fail.")
        B_name = self.rand_str()
        cidr_address = "192.22.2.1/24"
        start = "192.22.3.1"
        end = "192.22.3.2"
        self.bridge_body["networkMode"] = "dnsmasq"
        self.bridge_body["setting"] = {"cidr": cidr_address, "start": start, "end": end}
        self.bridge_body["name"] = B_name
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": B_name})
        self.assertEqual(response.status_code, 400, response.content)

    def test011_create_bridge_with_invalid_settings_in_dnsmasq(self):
        """ GAT-111
        *Create bridge with dnsmasq network mode and invalid settings. *

        **Test Scenario:**

        #.Create bridge (B0) with dnsmasq network mode and empty setting value,should fail.
        #.Create bridge (B1) with dnsmasq network and empty start and end values, should fail.

        """
        self.lg.info(" Create bridge (B0) with dnsmasq network mode and empty setting value,should fail.")
        B0_name = self.rand_str()
        self.bridge_body["name"] = B0_name
        self.bridge_body["networkMode"] = "dnsmasq"
        self.bridge_body["setting"] = {}
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": B0_name})
        self.assertEqual(response.status_code, 400, response.content)

        self.lg.info(" Create bridge (B1) with dnsmasq network and empty start and end values, should fail.")
        B1_name = self.rand_str()
        cidr_address = "192.22.3.5/24"
        self.bridge_body["name"] = B1_name
        self.bridge_body["networkMode"] = "dnsmasq"
        self.bridge_body["setting"] = {"cidr": cidr_address}
        response = self.bridges_api.post_nodes_bridges(self.nodeid, self.bridge_body)
        self.createdbridges.append({"node": self.nodeid, "name": B1_name})
        self.assertEqual(response.status_code, 400, response.content)
