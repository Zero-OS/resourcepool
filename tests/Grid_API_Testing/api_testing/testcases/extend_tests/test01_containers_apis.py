import random
import time
import unittest
from api_testing.testcases.testcases_base import TestcasesBase
from api_testing.python_client.client import Client
from api_testing.grid_apis.apis.nodes_apis import NodesAPI
from api_testing.grid_apis.apis.containers_apis import ContainersAPI
import json
from api_testing.grid_apis.apis.bridges_apis import BridgesAPI
from api_testing.grid_apis.apis.storagepools_apis import StoragepoolsAPI
from urllib.request import urlopen


class TestcontaineridAPI(TestcasesBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridges_api = BridgesAPI()
        self.storagepool_api = StoragepoolsAPI()

        self.createdcontainer=[]

    def setUp(self):
        self.lg.info('Choose one random node of list of running nodes.')
        self.node_id = self.get_random_node()
        if self.node_id is None:
            self.lg.info(' No node found')
            return
        self.node = {}
        for node in self.nodes:
            if node['id'] == self.node_id:
                self.g8os_ip = node['ip']
                self.node = node
                break
        self.g8core = Client(self.g8os_ip)
        self.root_url = "https://hub.gig.tech/gig-official-apps/ubuntu1604.flist"
        self.storage = "ardb://hub.gig.tech:16379"
        self.container_name = self.rand_str()
        self.hostname = self.rand_str()
        self.process_body = {'name': 'yes'}
        self.container_body = {"name": self.container_name, "hostname": self.hostname, "flist": self.root_url,
                               "hostNetworking": False, "initProcesses": [], "filesystems": [],
                               "ports": [], "storage": self.storage
                               }

    def tearDown(self):
        self.lg.info('TearDown:delete all created container ')
        for container in self.createdcontainer:
            self.containers_api.delete_containers_containerid(container['node'],
                                                              container['container'])

    def test001_check_coonection_with_False_hostNetworking(self):
        """ GAT-082
        *Check container internet connection with false hostNetworking options *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Create container with false hostNetworking.
        #. Try to connect to internet from created container ,Should fail.

        """
        self.lg.info('Send post nodes/{nodeid}/containers api request.')
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.lg.info('Make sure it running .')
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=self.container_name))
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})

        self.lg.info("Try to connect to internet from created container ,Should fail.")
        container = self.g8core.get_container_client(self.container_name)
        self.assertTrue(container)
        response = container.bash('ping -c 5 google.com').get()
        self.assertEqual(response.state, 'ERROR')

    def test002_check_coonection_with_True_hostNetworking(self):
        """ GAT-083
        *Check container internet connection with true hostNetworking options *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Create container with True hostNetworking.
        #. Try to connect to internet from created container ,Should succeed.

        """
        self.container_body['hostNetworking']=True

        self.lg.info('Send post nodes/{nodeid}/containers api request.')
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('Make sure it is running .')
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=self.container_name))
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})

        self.lg.info("Try to connect to internet from created container ,Should succeed.")
        container = self.g8core.get_container_client(self.container_name)
        self.assertTrue(container)
        response = container.bash('ping -c 5 google.com').get()
        self.assertEqual(response.state, 'SUCCESS')
        self.assertNotIn("unreachable", response.stdout)

    def test003_create_container_with_init_process(self):
        """ GAT-084
        *Check that container created with init process *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Create container with initProcess.
        #. Check that container created with init process.

        """
        self.container_body['flist']="https://hub.gig.tech/dina_magdy/initprocess.flist"
        ## flist which have script which print environment varaibles and print stdin
        Environmentvaraible = "MYVAR=%s"%self.rand_str()
        stdin = self.rand_str()
        self.container_body['initProcesses'] = [{"name": "sh", "pwd": "/",
                                                 "args": ["sbin/process_init"],
                                                 "environment":["%s"%Environmentvaraible],
                                                 "stdin":"%s"%stdin}]

        self.lg.info('Send post nodes/{nodeid}/containers api request.')
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('Make sure it running')
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=self.container_name))
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})

        self.lg.info("Check that container created with init process.")
        container = self.g8core.get_container_client(self.container_name)
        response = container.bash("ls |grep  out.text").get()
        self.assertEqual(response.state, "SUCCESS")
        response = container.bash("cat out.text | grep %s"%stdin).get()
        self.assertEqual(response.state, "SUCCESS", "init processes didn't get stdin correctly")
        response = container.bash("cat out.text | grep %s"%Environmentvaraible).get()
        self.assertEqual(response.state, "SUCCESS", "init processes didn't get Env varaible  correctly")

    def test004_create_containers_with_different_flists(self):
        """ GAT-085
        *create contaner with different flists *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Choose one random flist .
        #. Create container with this flist, Should succeed.
        #. Make sure it created with required values, should succeed.
        #. Make sure that created container is running,should succeed.
        #. Check that container created on node, should succeed
        """
        flistslist = ["ovs.flist", "ubuntu1604.flist", "grid-api-flistbuild.flist",
                      "cloud-init-server-master.flist"]

        flist = random.choice(flistslist)
        self.container_body['flist']="https://hub.gig.tech/gig-official-apps/%s"%flist
        self.lg.info('Send post nodes/{nodeid}/containers api request.')
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('Make sure it created with required values and running, should succeed.')
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=self.container_name))
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})
        response = self.containers_api.get_containers_containerid(self.node_id, self.container_name)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        for key in response_data.keys():
            if key == 'initprocesses':
                self.assertEqual(response_data[key], self.container_body['initProcesses'])
                continue
            if key in self.container_body.keys():
                self.assertEqual(response_data[key], self.container_body[key])

        self.lg.info("check that container created on node, should succeed")
        self.assertTrue(self.g8core.client.container.find(self.container_name))


    @unittest.skip("https://github.com/g8os/core0/issues/228")
    def test005_Check_container_access_to_host_dev(self):
        """ GAT-086
        *Make sure that container doesn't have access to host dev files *

        **Test Scenario:**

        #. Create container, Should succeed.
        #. Make sure that created container is running,should succeed.
        #. Check that container doesn't has access to host dev files .

        """

        self.lg.info('Send post nodes/{nodeid}/containers api request.')
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)

        self.lg.info('Make sure it created with required values and running, should succeed.')
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=self.container_name))
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})

        self.lg.info("Check that container doesn't has access to host dev files .")
        container = self.g8core.get_container_client(self.container_name)
        response = container.bash("ls -alh").get().stdout
        for line in response.splitlines():
            if "dev" in line:
                self.assertNotIn('w', line)

    def test006_create_container_with_bridge(self):
        """ GAT-087
        *Test case for create containers with same bridge and make sure they can connect to each other *

        **Test Scenario:**

        #. Create bridge with dnsmasq network , should succeed.
        #. Create 2 containers C1, C2 with created bridge, should succeed.
        #. Check if each container (C1), (C2) got an ip address, should succeed.
        #. Check if first container (c1) can ping second container (c2), should succeed.
        #. Check if second container (c2) can ping first container (c1), should succeed.
        #. Check that two containers get ip and they are in bridge range, should succeed.
        #. Delete created bridge .

        """

        self.lg.info('Create bridge with dnsmasq network, should succeed')
        bridge_name = self.rand_str()
        hwaddr = self.randomMAC()
        ip_range = ["201.100.2.1", "201.100.2.2"]
        body = {"name": bridge_name,
                "hwaddr": hwaddr,
                "networkMode": "dnsmasq",
                "nat": False,
                "setting": {"cidr":"201.100.2.0/8", "start": ip_range[0], "end": ip_range[1]}}

        response = self.bridges_api.post_nodes_bridges(self.node_id, body)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        self.lg.info('Create 2 containers C1, C2 with created bridge, should succeed.')
        nics = [{"type": "bridge", "id": bridge_name, "config": {"dhcp":True}, "status": "up" }]
        self.container_body["nics"] = nics
        C1_name = self.rand_str()
        C2_name = self.rand_str()

        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running",
                                                       self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C1_name))
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})


        self.container_body["name"] = C2_name
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name))
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})

        self.lg.info("Get two containers client C1_client and C2_client .")
        C1_client = self.g8core.get_container_client(C1_name)
        C2_client = self.g8core.get_container_client(C2_name)

        self.lg.info("Check that two containers get ip and they are in bridge range, should succeed ")
        C1_br_ip = self.g8core.get_container_bridge_ip(C1_client, ip_range)
        C2_br_ip = self.g8core.get_container_bridge_ip(C2_client, ip_range)
        self.assertNotEqual(C2_br_ip, C1_br_ip)

        self.lg.info("Check if first container (c1) can ping second container (c2), should succeed.")
        response = C1_client.bash('ping -c 10 %s'%C2_br_ip).get()
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info("Check if second container (c2) can ping first container (c1), should succeed.")
        response = C2_client.bash('ping -c 10 %s'%C1_br_ip).get()
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info("Create C3 without bridge ")
        C3_name = self.rand_str()
        nics = []
        self.container_body["name"] = C3_name
        self.container_body["nics"] = nics

        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                        nodeid=self.node_id,
                                                        containername=C3_name))
        self.createdcontainer.append({"node": self.node_id, "container": C3_name})
        C3_client = self.g8core.get_container_client(C3_name)

        self.lg.info("Check if third container (c3) can ping first container (c1), should fail.")
        response = C3_client.bash('ping -c 10 %s'%C1_br_ip).get()
        self.assertEqual(response.state, 'ERROR')

        self.lg.info("Delete created bridge ")
        self.bridges_api.delete_nodes_bridges_bridgeid(self.node_id, bridge_name)

    def test007_create_containers_with_diff_bridges(self):
        """ GAT-088
        *Test case for create containers with different bridges and make sure they can't connect to  each other through bridge ip *

        **Test Scenario:**

        #. Create 2 bridges (B1),(B2) with dnsmasq network , should succeed.
        #. Create container(C1) with (B1), should succeed.
        #. Create container(C2) with (B2), should succeed.
        #. Check if each container (C1), (C2) got an ip address, should succeed.
        #. Check if first container (c1) can ping second container (c2), should fail .
        #. Check if second container (c2) can ping first container (c1), should fail.
        #. Delete created bridges .

        """

        self.lg.info('Create bridged (B1),(B2) with dnsmasq network, should succeed')
        B1_name = self.rand_str()
        B2_name = self.rand_str()
        hwaddr1 = self.randomMAC()
        hwaddr2 = self.randomMAC()
        cidr1 = "198.101.5.0"
        cidr2 = "201.100.2.1"
        ip_range1 = ["198.101.5.1", "198.101.5.2"]
        ip_range2 = ["201.100.2.1", "201.100.2.2"]

        body1 = {"name": B1_name,
                "hwaddr": hwaddr1,
                "networkMode": "dnsmasq",
                "nat": False,
                "setting": {"cidr":"%s/8"%cidr1, "start": ip_range1[0], "end": ip_range1[1]}}

        body2 = {"name": B2_name,
                "hwaddr": hwaddr2,
                "networkMode": "dnsmasq",
                "nat": False,
                "setting": {"cidr":"%s/8"%cidr2, "start": ip_range2[0], "end": ip_range2[1]}}

        response = self.bridges_api.post_nodes_bridges(self.node_id, body1)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        response = self.bridges_api.post_nodes_bridges(self.node_id, body2)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        self.lg.info('Create container(C1) with (B1), should succeed.')
        nics1 = [{"type": "bridge", "id": B1_name, "config": {"dhcp":True}, "status": "up" }]
        self.container_body["nics"] = nics1
        C1_name = self.rand_str()
        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                        nodeid=self.node_id,
                                                        containername=C1_name))
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})

        self.lg.info('Create container(C2) with (B2), should succeed.')
        nics2 = [{"type": "bridge", "id": B2_name, "config": {"dhcp":True}, "status": "up" }]
        self.container_body["nics"] = nics2
        C2_name = self.rand_str()
        self.container_body["name"] = C2_name

        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name))
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})

        self.lg.info("Get two containers client C1_client and C2_client .")
        C1_client = self.g8core.get_container_client(C1_name)
        C2_client = self.g8core.get_container_client(C2_name)

        self.lg.info("Check that two containers get ip and they are in bridge range, should succeed ")
        C1_br_ip = self.g8core.get_container_bridge_ip(C1_client, ip_range1)
        C2_br_ip = self.g8core.get_container_bridge_ip(C2_client, ip_range2)

        self.lg.info("Check if first container (c1) can ping second container (c2), should fail.")
        response = C1_client.bash('ping -w 5 %s'%C2_br_ip).get()
        self.assertEqual(response.state, 'ERROR')

        self.lg.info("Check if second container (c2) can ping first container (c1), should fail.")
        response = C2_client.bash('ping -w 5 %s'%C1_br_ip).get()
        self.assertEqual(response.state, 'ERROR')

        self.lg.info("Delete created bridge ")
        self.bridges_api.delete_nodes_bridges_bridgeid(self.node_id, B2_name)
        self.bridges_api.delete_nodes_bridges_bridgeid(self.node_id, B1_name)

    def test008_Create_container_with_zerotier_network(self):
        """ GAT-089
        *Test case for create containers with same zerotier network *

        **Test Scenario:**
        #. Create Zerotier network using zerotier api ,should succeed.
        #. Create two containers C1,C2 with same zertoier networkId, should succeed.
        #. Check that two containers get zerotier ip, should succeed.
        #. Make sure that two containers can connect to each other, should succeed.

        """

        Z_Id = self.create_zerotier_network()

        self.lg.info('Create 2 containers C1, C2 with same zerotier network Id , should succeed')
        nic = [{'type': 'default'}, {'type': 'zerotier', 'id': Z_Id}]
        self.container_body["nics"] = nic
        C1_name = self.rand_str()
        C2_name = self.rand_str()

        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C1_name))
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})

        self.container_body["name"] = C2_name
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name))
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})

        self.lg.info("Get two containers client C1_client and C2_client .")
        C1_client = self.g8core.get_container_client(C1_name)
        C2_client = self.g8core.get_container_client(C2_name)

        self.lg.info("Check that two containers get zerotier ip, should succeed ")
        time.sleep(5)
        C1_Zt_ip = self.g8core.get_client_zt_ip(C1_client)
        self.assertTrue(C1_Zt_ip)
        C2_Zt_ip = self.g8core.get_client_zt_ip(C2_client)
        self.assertTrue(C2_Zt_ip)

        self.lg.info("first container C1 ping second container C2 ,should succeed")
        response = C1_client.bash('ping -c 5 %s'%C2_Zt_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("second container C2 ping first container C1 ,should succeed")
        response = C2_client.bash('ping -c 5 %s'%C1_Zt_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("Create C3 without zerotier ")
        C3_name = self.rand_str()
        nics = []
        self.container_body["name"] = C3_name
        self.container_body["nics"] = nics

        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C3_name))
        self.createdcontainer.append({"node": self.node_id, "container": C3_name})
        C3_client = self.g8core.get_container_client(C3_name)

        self.lg.info("Check if third container (c3) can ping first container (c1), should fail.")
        response = C3_client.bash('ping -c 10 %s'%C1_Zt_ip).get()
        self.assertEqual(response.state, 'ERROR')

        self.lg.info("Delete zerotier network ")
        self.delete_zerotier_network(Z_Id)

    def test009_create_containers_with_vlan_network(self):
        """ GAT-090

        *Test case for test creation of containers with vlan network*

        **Test Scenario:**

        #. Create ovs container .
        #. Create two containers with same vlan tag, should succeed.
        #. Check that two containers get correct vlan ip, should succeed.
        #. First container C1 ping second container C2 ,should succeed.
        #. Second container C2 ping first container C1 ,should succeed.
        #. Create C3 with different vlan tag , should succeed.
        #. Check if third container (c3) can ping first container (c1), should fail.

        """
        self.lg.info("create ovs container")
        self.g8core.create_ovs_container()

        self.lg.info("create two container with same vlan tag,should succeed")

        vlan1_id = random.randint(1, 2000)
        C1_ip = "201.100.2.0"
        C2_ip = "201.100.3.0"

        C1_name = self.rand_str()
        nic = [{'type': 'default'}, {'type': 'vlan', 'id': "%s"%vlan1_id, 'config': {'cidr':'%s/24'%C1_ip}}]
        self.container_body["nics"] = nic
        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(self.node_id,self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C1_name))
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})

        C2_name = self.rand_str()
        self.container_body["name"] = C2_name
        nic = [{'type': 'default'}, {'type': 'vlan', 'id': "%s"%vlan1_id, 'config': {'cidr':'%s/24'%C2_ip}}]
        self.container_body["nics"] = nic
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name))
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})

        self.lg.info("Get two containers client C1_client and C2_client.")
        C1_client = self.g8core.get_container_client(C1_name)
        C2_client = self.g8core.get_container_client(C2_name)

        self.lg.info("Check that two containers get correct vlan ip, should succeed ")
        self.assertTrue(self.g8core.check_container_vlan_vxlan_ip(C1_client, C1_ip))
        self.assertTrue(self.g8core.check_container_vlan_vxlan_ip(C2_client, C2_ip))

        self.lg.info("first container C1 ping second container C2 ,should succeed")
        response = C1_client.bash('ping -w 2 %s'%C1_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("second container C2 ping first container C1 ,should succeed")
        response = C2_client.bash('ping -w 2 %s'%C2_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("Create C3 with different vlan tag ")
        vlan2_id = random.randint(2001, 4096)
        C3_ip = "200.200.4.0"
        C3_name = self.rand_str()
        nic = [{'type': 'default'}, {'type': 'vlan', 'id': "%s"%vlan2_id, 'config': {'cidr':'%s/24'%C3_ip}}]
        self.container_body["nics"] = nic
        self.container_body["name"] = C3_name
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C3_name))
        self.createdcontainer.append({"node": self.node_id, "container": C3_name})
        C3_client = self.g8core.get_container_client(C3_name)
        self.assertTrue(C3_client)

        self.lg.info("Check if third container (c3) can ping first container (c1), should fail.")
        response = C3_client.bash('ping -w 2 %s'%C1_ip).get()
        self.assertEqual(response.state, 'ERROR')

    def test010_create_containers_with_vxlan_network(self):
        """ GAT-091

        *Test case for test creation of containers with vxlan network*

        **Test Scenario:**

        #. Create ovs container .
        #. Create two containers with same vxlan tag, should succeed.
        #. Check that two containers get correct vxlan ip, should succeed.
        #. First container C1 ping second container C2 ,should succeed.
        #. Second container C2 ping first container C1 ,should succeed.
        #. Create third container c3 with different vxlan Id,should succeed
        #. Check if third container (c3) can ping first container (c1), should fail.
        """
        self.lg.info("create ovs container")
        self.g8core.create_ovs_container()

        self.lg.info("create two container with same vxlan id,should succeed")

        vxlan1_id = random.randint(5000, 6000)
        C1_ip = "201.100.2.0"
        C2_ip = "201.100.3.0"

        C1_name = self.rand_str()
        nic = [{'type': 'default'}, {'type': 'vxlan', 'id': "%s"%vxlan1_id, 'config': {'cidr':'%s/24'%C1_ip}}]
        self.container_body["nics"] = nic
        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C1_name))
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})
        C2_name = self.rand_str()
        self.container_body["name"] = C2_name
        nic = [{'type': 'default'}, {'type': 'vxlan', 'id': "%s"%vxlan1_id, 'config': {'cidr':'%s/24'%C2_ip}}]
        self.container_body["nics"] = nic
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name))
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})

        self.lg.info("Get two containers client C1_client and C2_client.")
        C1_client = self.g8core.get_container_client(C1_name)
        C2_client = self.g8core.get_container_client(C2_name)

        self.lg.info("Check that two containers get correct vxlan ip, should succeed ")
        self.assertTrue(self.g8core.check_container_vlan_vxlan_ip(C1_client, C1_ip))
        self.assertTrue(self.g8core.check_container_vlan_vxlan_ip(C2_client, C2_ip))

        self.lg.info("first container C1 ping second container C2 ,should succeed")
        response = C1_client.bash('ping -w 5 %s'%C1_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("second container C2 ping first container C1 ,should succeed")
        response = C2_client.bash('ping -w 5 %s'%C2_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("Create third container c3 with different vxlan Id,should succeed")
        vxlan2_id = random.randint(7000, 8000)
        C3_ip = "200.200.4.0"
        C3_name = self.rand_str()
        nic = [{'type': 'default'}, {'type': 'vxlan', 'id': "%s"%vxlan2_id, 'config': {'cidr':'%s/24'%C3_ip}}]
        self.container_body["nics"] = nic
        self.container_body["name"] = C3_name
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C3_name))
        self.createdcontainer.append({"node": self.node_id, "container": C3_name})
        C3_client = self.g8core.get_container_client(C3_name)
        self.assertTrue(C3_client)

        self.lg.info("Check if third container (c3) can ping first container (c1), should fail.")
        response = C3_client.bash('ping -w 5 %s'%C1_ip).get()
        self.assertEqual(response.state, 'ERROR')

    @unittest.skip("https://github.com/g8os/resourcepool/pull/293")
    def test011_create_containers_with_gateway_network_in_config(self):
        """ GAT-092

        *Test case for test creation of containers with gateway in configeration  *

        **Test Scenario:**

        #. create container (C1) with type default in nic , should succeed
        #. create container (C2) with type vlan and gateway in nic, should succeed
        #. Check that C1  can ping second container C2 , should fail.
        #. Check that C1  can ping second container C2 through its gateway, should succeed.

        """

        self.lg.info("create ovs container")
        self.g8core.create_ovs_container()

        self.lg.info("create container (C1) with type default in nic, should succeed")
        C1_name = self.rand_str()
        nic = [{'type': 'default'}]
        dns = ['8.8.8.8']
        self.container_body["nics"] = nic
        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C1_name))
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})

        self.lg.info("create container (C2) with type vlan and gatway in nic, should succeed")
        C_ip = "201.100.2.0"
        gateway = "192.189.1.2"
        vlan_Id = random.randint(1,4096)
        C2_name = self.rand_str()
        self.container_body["name"] = C2_name
        nic = [{'type': 'default'},
               {'type': 'vlan', 'id': "%s"%vlan_Id, 'config': {'cidr':'%s/24'%C_ip,'gateway':'%s'%gateway}}]
        self.container_body["nics"] = nic
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name))
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})
        C1_client = self.g8core.get_container_client(C1_name)
        C2_client = self.g8core.get_container_client(C2_name)

        self.lg.info("Check that C1  can ping second container C2 , should fail.")
        response = C1_client.bash("ping -w2 %s "%C_ip).get()
        self.assertEqual(response.state, "ERROR")

        self.lg.info("Check that C1  can ping second container C2 through its gateway, should succeed.")
        response = C1_client.bash("ping -w2 %s "%gateway).get()
        self.assertEqual(response.state, "SUCCESS")

    def test012_create_container_with_dns_in_config(self):
        """ GAT-093

        *Test case for test creation of containers with different network and with dns *

        **Test Scenario:**

        #. Create container (C1) with type default in nic with dns.
        #. Check if values of dns in /etc/resolve.conf ,should fail .
        #. Create container (c2) with vlan and with dns .
        #. Check if values of dns in /etc/resolve.conf ,should succeed .

        """

        self.lg.info("create ovs container")
        self.g8core.create_ovs_container()

        self.lg.info("create container (C1) with type default in nic with dns , should succeed")

        C1_name = self.rand_str()
        dns = '8.8.4.4'
        cidr = "192.125.2.1"
        nic = [{'type': 'default', "config": {"cidr": "%s/8"%cidr, "dns": ["%s"%dns]}}]
        self.container_body["nics"] = nic
        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C1_name))
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})

        self.lg.info("Check if values of dns in /etc/resolve.conf ,should fail")
        C1_client = self.g8core.get_container_client(C1_name)
        response = C1_client.bash('cat /etc/resolv.conf | grep %s'%dns).get()
        self.assertEqual(response.state,"ERROR")

        self.lg.info(" Create container (c2) with vlan and with dns, should succeed")
        C_ip = "201.100.2.0"
        vlan_Id = random.randint(1,4096)
        C2_name = self.rand_str()
        self.container_body["name"] = C2_name
        nic = [{'type': 'default'},
               {'type': 'vlan', 'id': "%s"%vlan_Id, 'config': {'cidr':'%s/24'%C_ip,'dns':['%s'%dns]}}]
        self.container_body["nics"] = nic
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name))
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})

        self.lg.info("Check if values of dns in /etc/resolve.conf ,should succeed. ")
        C2_client = self.g8core.get_container_client(C2_name)
        response = C2_client.bash('cat /etc/resolv.conf | grep %s'%dns).get()
        self.assertEqual(response.state, "SUCCESS")
        response = C2_client.bash('ping -c 2 %s'%dns).get()
        self.assertEqual(response.state, "SUCCESS")

    def test013_create_container_with_filesystem(self):
        """ GAT-094

        *Test case for test creation of containers with filesystem. *

        **Test Scenario:**

        #. Create file system in fsucash storage pool.
        #. Create container with created file system,should succeed .
        #. Check that file exist in /fs/storagepool_name/filesystem_name ,should succeed .
        """

        self.lg.info("Create file system in fsucash storage pool")
        name = self.random_string()

        quota = random.randint(1, 100)
        body = {"name": name, "quota": quota}
        storagepool_name = "%s_fscache"%self.node_id
        response = self.storagepool_api.post_storagepools_storagepoolname_filesystems(self.node_id, storagepool_name, body)
        self.assertEqual(response.status_code, 201)
        time.sleep(5)

        self.lg.info("Create container with created file system,should succeed.")
        self.container_body["filesystems"].append("%s:%s"%(storagepool_name,name))
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=self.container_name, timeout=300))
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})

        self.lg.info("Check that file exist in /fs/storagepool_name/filesystem_name ,should succeed")
        C_client = self.g8core.get_container_client(self.container_name)
        response = C_client.filesystem.list('/fs/%s'%storagepool_name)
        self.assertEqual(response[0]['name'], name)

    def test014_Writing_in_containers_files(self):
        """ GAT-095

        *Test case for test writing in containner files *

        **Test Scenario:**

        #. Create two conainer  container C1,C2 ,should succeed.
        #. Create file in C1,should succeed.
        #. Check that created file doesn't exicst in C2.

        """
        self.lg.info("Create two conainer  container C1,C2 ,should succeed.")
        C1_name = self.rand_str()
        C2_name = self.rand_str()
        self.container_body["name"] = C1_name
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertTrue(response.status_code,201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C1_name),
                                                       "container %s status is halted"%self.container_name)
        self.createdcontainer.append({"node": self.node_id, "container": C1_name})

        C2_name=self.rand_str()
        self.container_body["name"] = C2_name
        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertTrue(response.status_code,201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=C2_name),
                                                       "container %s status is halted"%self.container_name)
        self.createdcontainer.append({"node": self.node_id, "container": C2_name})
        C1_client = self.g8core.get_container_client(C1_name)
        C2_client = self.g8core.get_container_client(C2_name)

        self.lg.info("Create file in C1,should succeed.")
        file_name = self.rand_str()
        response = C1_client.bash("touch %s"%file_name).get()
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info("Check that created file doesn't exicst in C2.")

        response = C1_client.bash("ls | grep %s"%file_name).get()
        self.assertEqual(response.state, 'SUCCESS')

        response = C2_client.bash("ls | grep %s"%file_name).get()
        self.assertEqual(response.state, 'ERROR')

    def test015_create_containers_with_open_ports(self):
        """ GAT-096

        *Test case for test create containers with open ports*

        **Test Scenario:**

        #. Create container C1 with open port .
        #. Open server in container port ,should succeed.
        #. Check that portforward work,should succeed
        """

        file_name = self.rand_str()
        hostport="6060"
        containerport="60"
        ports = "%s:%s"%(hostport,containerport)
        nics = [{"type": "default"}]
        self.container_body["nics"]=nics
        self.container_body["ports"].append(ports)

        self.lg.info("Create container C1 with open port")
        response = self.containers_api.post_containers(self.node_id, self.container_body)
        self.assertTrue(response.status_code,201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                        nodeid=self.node_id,
                                                        containername=self.container_name),
                                                        "container %s status is halted"%self.container_name)
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})
        C1_client = self.g8core.get_container_client(self.container_name)
        self.g8core.timeout = 300
        time.sleep(2)
        self.lg.info("Open server in container port ,should succeed")
        response = C1_client.bash("apt-get -y install python ").get()
        self.assertEqual(response.state, "SUCCESS")
        response = C1_client.bash("mkdir {0} && cd {0}&& echo 'test'>{0}.text ".format(file_name)).get()
        self.assertEqual(response.state, "SUCCESS")
        C1_client.bash("cd %s &&  nohup python -m SimpleHTTPServer %s & "%(file_name,containerport))

        self.lg.info("Check that portforward work,should succeed")
        response = C1_client.bash("netstat -nlapt | grep %s"%containerport).get()
        self.assertEqual(response.state, 'SUCCESS')
        url=' http://{0}:{1}/{2}.text'.format(self.g8os_ip,hostport,file_name)
        response = urlopen(url)
        html = response.read()
        self.assertIn("test",html.decode('utf-8'))

    @unittest.skip("https://github.com/g8os/resourcepool/issues/297")
    def test016_post_new_job_to_container_with_specs(self):
        """ GAT-097

        *Test case for test create containers with open ports*

        **Test Scenario:**

        #. Create containers C1 , should succeed
        #. post job with to container with all specs ,should succeed.
        #. check that job created successfully with it's specs.

        """
        self.lg.info("Create container C1, should succeed.")
        self.container_body['flist']="https://hub.gig.tech/dina_magdy/initprocess.flist"
        ## flist which have script which print environment varaibles and print stdin
        Environmentvaraible = "MYVAR=%s"%self.rand_str()
        stdin = self.rand_str()
        job_body = {
                    'name': 'sh',
                    'pwd': '/',
                    'args': ["sbin/process_init"],
                    "environment":["%s"%Environmentvaraible],
                    "stdin":"%s"%stdin
                    }

        response = self.containers_api.post_containers(nodeid=self.node_id, data=self.container_body)
        self.assertTrue(response.status_code,201)
        self.assertTrue(self.wait_for_container_status("running", self.containers_api.get_containers_containerid,
                                                       nodeid=self.node_id,
                                                       containername=self.container_name),
                                                       "container %s status is halted"%self.container_name)
        self.createdcontainer.append({"node": self.node_id, "container": self.container_name})
        C1_client = self.g8core.get_container_client(self.container_name)

        self.lg.info('Send post  nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.post_containers_containerid_jobs(self.node_id, self.container_name,
                                                                        job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.g8core.wait_on_container_job_update(self.container_name, job_id, 15, False))

        self.lg.info("check that job created successfully with it's specs.")
        response = C1_client.bash("ls |grep  out.text").get()
        self.assertEqual(response.state, "SUCCESS")
        response = C1_client.bash("cat out.text | grep %s"%stdin).get()
        self.assertEqual(response.state, "SUCCESS", "job didn't get stdin correctly")
        response = C1_client.bash("cat out.text | grep %s"%Environmentvaraible).get()
        self.assertEqual(response.state, "SUCCESS", "job didn't get Env varaible  correctly")
