import random, time, unittest
from testcases.testcases_base import TestcasesBase
from urllib.request import urlopen
import requests
import json

class TestcontaineridAPI(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.process_body = {'name': 'yes'}
        self.created = {'bridge': [],
                        'container': []}

    def tearDown(self):
        self.lg.info('TearDown:delete all created containers and bridges')
        for container_name in self.created['container']:
            self.containers_api.delete_containers_containerid(self.nodeid, container_name)
        for bridge_name in self.created['bridge']:
            self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, bridge_name)

    def test001_check_coonection_with_False_hostNetworking(self):
        """ GAT-082
        *Check container internet connection with false hostNetworking options *

        **Test Scenario:**

        #. Choose one random node of list of running nodes.
        #. Create container with false hostNetworking.
        #. Try to connect to internet from created container ,Should fail.

        """
        self.lg.info(' [*] Create new container. ')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        self.created['container'].append(self.data['name'])

        self.lg.info(" [*] Try to connect to internet from created container , Should fail.")
        container = self.core0_client.get_container_client(self.data['name'])
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
        self.lg.info(' [*] Create new container. ')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid, hostNetworking=True)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        self.created['container'].append(self.data['name'])

        self.lg.info("Try to connect to internet from created container ,Should succeed.")
        container = self.core0_client.get_container_client(self.data['name'])
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
        flist = "https://hub.gig.tech/dina_magdy/initprocess.flist"
        initProcesses = [{"name": "sh", "pwd": "/",
                          "args": ["sbin/process_init"],
                          "environment": ["MYVAR=%s" % self.rand_str()],
                          "stdin": self.rand_str()}]
        self.lg.info(' [*] Create new container. ')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid,
                                                                       flist=flist,
                                                                       initProcesses=initProcesses)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        self.created['container'].append(self.data['name'])

        self.lg.info(" [*] Check that container created with init process.")
        container = self.core0_client.get_container_client(self.data['name'])
        response = container.bash("ls |grep  out.text").get()
        self.assertEqual(response.state, "SUCCESS")
        response = container.bash("cat out.text | grep %s" % self.data['initProcesses'][0]['stdin']).get()
        self.assertEqual(response.state, "SUCCESS", "init processes didn't get stdin correctly")
        response = container.bash("cat out.text | grep %s" % self.data['initProcesses'][0]['environment']).get()
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

        flist = "https://hub.gig.tech/gig-official-apps/%s" % random.choice(flistslist)
        self.lg.info(' [*] Create new container. ')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid,
                                                                       flist=flist)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        self.created['container'].append(self.data['name'])

        response = self.containers_api.get_containers_containerid(self.nodeid, self.data['name'])
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        for key in response_data.keys():
            if key == 'initprocesses':
                self.assertEqual(response_data[key], self.data['initProcesses'])
            if key in self.data.keys():
                self.assertEqual(response_data[key], self.data[key])

        self.lg.info("check that container created on node, should succeed")
        self.assertTrue(self.core0_client.client.container.find(self.data['name']))

    def test005_Check_container_access_to_host_dev(self):
        """ GAT-086
        *Make sure that container dev is not shared with the core0 dev *

        **Test Scenario:**

        #. Create container, Should succeed.
        #. Make sure that created container is running,should succeed.
        #. Check that container dev is not shared with the core0 dev.

        """
        self.lg.info(' [*] Create new container. ')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        self.created['container'].append(self.data['name'])

        self.lg.info("Check that container dev is not shared with the core0 dev")
        container = self.core0_client.get_container_client(self.data['name'])
        cont_res = container.bash("ls -alh | grep dev").get().stdout
        core0_res = self.core0_client.client.bash('ls -alh | grep dev').get().stdout
        self.assertNotEqual(core0_res.split()[7], cont_res.split()[7])

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
        response, data_bridge = self.bridges_api.post_nodes_bridges(node_id=self.nodeid, networkMode='dnsmasq',
                                                                    nat=False)
        self.assertEqual(response.status_code, 201, response.content)
        self.created['bridge'].append(data_bridge['name'])
        ip_range = [data_bridge['setting']['start'], data_bridge['setting']['end']]


        self.lg.info(' [*] Create 2 containers C1, C2 with created bridge, should succeed.')
        nics = [{"type": "bridge", "id": data_bridge['name'], "config": {"dhcp": True}, "status": "up"}]
        response_cont_1, data_cont_1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics)
        self.assertEqual(response_cont_1.status_code, 201, " [*] Can't create new container.")
        self.created['container'].append(data_cont_1['name'])

        response_cont_2, data_cont_2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics)
        self.assertEqual(response_cont_2.status_code, 201, " [*] Can't create new container.")
        self.created['container'].append(data_cont_2['name'])

        self.lg.info("Get two containers client c1_client and c2_client .")
        c1_client = self.core0_client.get_container_client(data_cont_1['name'])
        c2_client = self.core0_client.get_container_client(data_cont_2['name'])

        self.lg.info("Check that two containers get ip and they are in bridge range, should succeed ")
        C1_br_ip = self.core0_client.get_container_bridge_ip(c1_client, ip_range)
        C2_br_ip = self.core0_client.get_container_bridge_ip(c2_client, ip_range)
        self.assertNotEqual(C2_br_ip, C1_br_ip)

        self.lg.info("Check if first container (c1) can ping second container (c2), should succeed.")
        time.sleep(5)
        response = c1_client.bash('ping -w5 %s' % C2_br_ip).get()
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info("Check if second container (c2) can ping first container (c1), should succeed.")
        response = c2_client.bash('ping -w5 %s' % C1_br_ip).get()
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info("Create C3 without bridge ")
        response_cont_3, data_cont_3 = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(response_cont_3.status_code, 201, " [*] Can't create new container.")
        C3_client = self.core0_client.get_container_client(data_cont_3['name'])
        self.created['container'].append(data_cont_3['name'])

        self.lg.info("Check if third container (c3) can ping first container (c1), should fail.")
        response = C3_client.bash('ping -w5 %s' % C1_br_ip).get()
        self.assertEqual(response.state, 'ERROR')

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
        response, data_bridge_1 = self.bridges_api.post_nodes_bridges(node_id=self.nodeid, networkMode='dnsmasq',
                                                                      nat=False)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)
        self.created['bridge'].append(data_bridge_1['name'])
        ip_range1 = [data_bridge_1['setting']['start'], data_bridge_1['setting']['end']]

        response, data_bridge_2 = self.bridges_api.post_nodes_bridges(node_id=self.nodeid, networkMode='dnsmasq',
                                                                      nat=False)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)
        self.created['bridge'].append(data_bridge_2['name'])
        ip_range2 = [data_bridge_1['setting']['start'], data_bridge_2['setting']['end']]

        self.lg.info(' [*] Create container(C1) with (B1), should succeed.')
        nics1 = [{"type": "bridge", "id": data_bridge_1['name'], "config": {"dhcp": True}, "status": "up"}]
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics1)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        self.lg.info(' [*] Create container(C2) with (B2), should succeed.')
        nics2 = [{"type": "bridge", "id": data_bridge_2['name'], "config": {"dhcp": True}, "status": "up"}]
        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics2)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

        self.lg.info(" [*] Get two containers client c1_client and c2_client .")
        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])

        self.lg.info(" [*] Check that two containers get ip and they are in bridge range, should succeed ")
        c1_br_ip = self.core0_client.get_container_bridge_ip(c1_client, ip_range1)
        c2_br_ip = self.core0_client.get_container_bridge_ip(c2_client, ip_range2)

        self.lg.info(" [*] Check if first container (c1) can ping second container (c2), should fail.")
        response = c1_client.bash('ping -w5 %s' % c2_br_ip).get()
        self.assertEqual(response.state, 'ERROR')

        self.lg.info(" [*] Check if second container (c2) can ping first container (c1), should fail.")
        response = c2_client.bash('ping -w5 %s' % c1_br_ip).get()
        self.assertEqual(response.state, 'ERROR')


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

        time.sleep(5)

        self.lg.info(' [*] Create 2 containers C1, C2 with same zerotier network Id , should succeed')
        nic = [{'type': 'default'}, {'type': 'zerotier', 'id': Z_Id}]
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

        self.lg.info(" [*] Get two containers client c1_client and c2_client .")
        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])

        time.sleep(15)

        self.lg.info(" [*] Check that two containers get zerotier ip, should succeed ")
        c1_zt_ip = self.core0_client.get_client_zt_ip(c1_client)
        self.assertTrue(c1_zt_ip)
        c2_zt_ip = self.core0_client.get_client_zt_ip(c2_client)
        self.assertTrue(c2_zt_ip)

        self.lg.info(" [*] first container C1 ping second container C2 ,should succeed")
        response = c1_client.bash('ping -w3 %s' % c2_zt_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info(" [*] second container C2 ping first container C1 ,should succeed")
        response = c2_client.bash('ping -w3 %s' % c1_zt_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info(" [*] Create C3 without zerotier ")
        response_c3, data_c3 = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(response_c3.status_code, 201)
        self.created['container'].append(data_c3['name'])
        C3_client = self.core0_client.get_container_client(data_c3['name'])

        self.lg.info(" [*] Check if third container (c3) can ping first container (c1), should fail.")
        response = C3_client.bash('ping -w3 %s' % c1_zt_ip).get()
        self.assertEqual(response.state, 'ERROR')

        self.lg.info(" [*] Delete zerotier network ")
        self.delete_zerotier_network(Z_Id)

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/892')
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
        self.lg.info(" [*] create ovs container")
        self.core0_client.create_ovs_container()

        self.lg.info(" [*] create two container with same vlan tag,should succeed")
        vlan1_id, vlan2_id = random.sample(range(1, 4096), 2)
        C1_ip = "201.100.2.1"
        C2_ip = "201.100.2.2"

        nic = [{'type': 'default'}, {'type': 'vlan', 'id': "%s" % vlan1_id, 'config': {'cidr': '%s/24' % C1_ip}}]
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        nic = [{'type': 'default'}, {'type': 'vlan', 'id': "%s" % vlan1_id, 'config': {'cidr': '%s/24' % C2_ip}}]
        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

        self.lg.info(" [*] Get two containers client c1_client and c2_client.")
        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])

        self.lg.info("Check that two containers get correct vlan ip, should succeed ")
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(c1_client, C1_ip))
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(c2_client, C2_ip))

        self.lg.info("first container C1 ping second container C2 ,should succeed")
        response = c1_client.bash('ping -w 2 %s' % C2_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("second container C2 ping first container C1 ,should succeed")
        response = c2_client.bash('ping -w 2 %s' % C1_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("Create C3 with different vlan tag ")
        C3_ip = "201.100.2.3"
        nic = [{'type': 'default'}, {'type': 'vlan', 'id': "%s" % vlan2_id, 'config': {'cidr': '%s/24' % C3_ip}}]
        response_c3, data_c3 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c3.status_code, 201)
        self.created['container'].append(data_c3['name'])

        C3_client = self.core0_client.get_container_client(data_c3['name'])
        self.assertTrue(C3_client)
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(C3_client, C3_ip))

        self.lg.info("Check if third container (c3) can ping first container (c1), should fail.")
        response = C3_client.bash('ping -w 2 %s' % C1_ip).get()
        self.assertEqual(response.state, 'ERROR')

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/892')
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
        self.core0_client.create_ovs_container()

        self.lg.info("create two container with same vxlan id,shoc3_nameuld succeed")

        vxlan1_id, vxlan2_id = random.sample(range(4096, 8000), 2)
        C1_ip = "201.100.3.1"
        C2_ip = "201.100.3.2"

        nic = [{'type': 'default'}, {'type': 'vxlan', 'id': "%s" % vxlan1_id, 'config': {'cidr': '%s/24' % C1_ip}}]
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        nic = [{'type': 'default'}, {'type': 'vxlan', 'id': "%s" % vxlan1_id, 'config': {'cidr': '%s/24' % C2_ip}}]
        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c2['name'])

        self.lg.info(" [*] Get two containers client c1_client and c2_client.")
        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])

        self.lg.info(" [*] Check that two containers get correct vxlan ip, should succeed ")
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(c1_client, C1_ip))
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(c2_client, C2_ip))

        self.lg.info(" [*] first container C1 ping second container C2 ,should succeed")
        response = c1_client.bash('ping -w 5 %s' % C2_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info(" [*] second container C2 ping first container C1 ,should succeed")
        response = c2_client.bash('ping -w 5 %s' % C1_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info(" [*] Create third container c3 with different vxlan Id,should succeed")
        C3_ip = "201.100.3.3"

        nic = [{'type': 'default'}, {'type': 'vxlan', 'id': "%s" % vxlan2_id, 'config': {'cidr': '%s/24' % C3_ip}}]
        response_c3, data_c3 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c3.status_code, 201)
        self.created['container'].append(data_c3['name'])

        C3_client = self.core0_client.get_container_client(data_c3['name'])
        self.assertTrue(C3_client)
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(C3_client, C3_ip))

        self.lg.info("Check if third container (c3) can ping (c1) and (c2), should fail.")
        response = C3_client.bash('ping -w 5 %s' % C1_ip).get()
        self.assertEqual(response.state, 'ERROR')
        response = C3_client.bash('ping -w 5 %s' % C2_ip).get()
        self.assertEqual(response.state, 'ERROR')

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/892')
    def test011_create_containers_with_gateway_network_in_config(self):
        """ GAT-092

        *Test case for test creation of containers with gateway in configeration  *

        **Test Scenario:**

        #. Create bridge (B0) with nat true and  with static network mode .
        #. Create container (C1) with (B0) without gateway.
        #. Create container (C2) with (B0) with gateway same ip of bridge.
        #. Check that (C1) can connect to internet, should fail.
        #. Check that (C2) can connect to internt, should succeed.

        """
        self.lg.info("create ovs container")
        self.core0_client.create_ovs_container()

        self.lg.info('Create bridge with static network and nat true , should succeed')
        response, data_bridge_1 = self.bridges_api.post_nodes_bridges(node_id=self.nodeid, networkMode='static',
                                                                      nat=True)
        self.created['bridge'].append(data_bridge_1['name'])
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        self.lg.info("Create container (C1) with (B0) without gateway.")
        nics = [{"type": "bridge", "id": data_bridge_1['name'], "config": {"cidr": "190.122.2.4/24"}, "status": "up"}]
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        self.lg.info("Create container (C2) with (B0) with gateway same ip of bridge.")
        nics = [{"type": "bridge", "id": data_bridge_1['name'],
                 "config": {"cidr": "192.122.2.3/24", "gateway": data_bridge_1['setting']['static']},
                 "status": "up"}]
        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])

        self.lg.info("Check that C1 can connect to internet, should fail.")
        response = c1_client.bash("ping -w 5  8.8.8.8").get()
        self.assertEqual(response.state, "ERROR", response.stdout)

        self.lg.info("Check that C2 can connect to internet, should fail.")
        response = c2_client.bash("ping -w 5 8.8.8.8").get()
        self.assertEqual(response.state, "SUCCESS", response.stdout)

        self.lg.info("Delete created bridge ")
        self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, data_bridge_1['name'])

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/892')
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
        self.core0_client.create_ovs_container()

        self.lg.info("create container (C1) with type default in nic with dns , should succeed")

        dns = '8.8.4.4'
        cidr = "192.125.2.1"
        nic = [{'type': 'default', "config": {"cidr": "%s/8" % cidr, "dns": ["%s" % dns]}}]
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        self.lg.info("Check if values of dns in /etc/resolve.conf ,should fail")
        c1_client = self.core0_client.get_container_client(data_c1['name'])
        response = c1_client.bash('cat /etc/resolv.conf | grep %s' % dns).get()
        self.assertEqual(response.state, "ERROR")

        self.lg.info(" Create container (c2) with vlan and with dns, should succeed")
        C_ip = "201.100.2.0"
        vlan_Id = random.randint(1, 4096)
        nic = [{'type': 'default'},
               {'type': 'vlan', 'id': "%s" % vlan_Id, 'config': {'cidr': '%s/24' % C_ip, 'dns': ['%s' % dns]}}]
        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

        self.lg.info("Check if values of dns in /etc/resolve.conf ,should succeed. ")
        c2_client = self.core0_client.get_container_client(data_c2['name'])
        response = c2_client.bash('cat /etc/resolv.conf | grep %s' % dns).get()
        self.assertEqual(response.state, "SUCCESS")
        response = c2_client.bash('ping -c 2 %s' % dns).get()
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
        storagepool_name = "%s_fscache" % self.nodeid
        response, data= self.storagepools_api.post_storagepools_storagepoolname_filesystems(self.nodeid, storagepool_name, **body)
        self.assertEqual(response.status_code, 201)

        self.lg.info("Create container with created file system,should succeed.")
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, filesystems=["%s:%s" % (storagepool_name, name)])
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        self.lg.info("Check that file exist in /fs/storagepool_name/filesystem_name ,should succeed")
        C_client = self.core0_client.get_container_client(data_c1['name'])
        response = C_client.filesystem.list('/fs/%s' % storagepool_name)
        self.assertEqual(response[0]['name'], name)

    def test014_Writing_in_containers_files(self):
        """ GAT-095

        *Test case for test writing in containner files *

        **Test Scenario:**

        #. Create two conainer  container C1,C2 ,should succeed.
        #. Create file in C1,should succeed.
        #. Check that created file doesn't exicst in C2.

        """
        self.lg.info(" [*] Create two conainer  container C1,C2 ,should succeed.")
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid)
        self.assertEqual(response_c2.status_code, 201)

        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])

        self.lg.info(" [*] Create file in C1,should succeed.")
        file_name = self.rand_str()
        response = c1_client.bash("touch %s" % file_name).get()
        self.assertEqual(response.state, 'SUCCESS')

        self.lg.info(" [*] Check that created file doesn't exicst in C2.")

        response = c1_client.bash("ls | grep %s" % file_name).get()
        self.assertEqual(response.state, 'SUCCESS')

        response = c2_client.bash("ls | grep %s" % file_name).get()
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
        hostport = 6060
        containerport = 60
        ports = "%i:%i" % (hostport, containerport)
        nics = [{"type": "default"}]

        # create rule on port 7070
        try:
            self.core0_client.client.nft.open_port(hostport)
        except:
            pass

        self.lg.info(" [*] Create container C1 with open port")
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics, ports=[ports])
        self.created['container'].append(data_c1['name'])
        self.assertEqual(response_c1.status_code, 201)

        c1_client = self.core0_client.get_container_client(data_c1['name'])
        self.core0_client.timeout = 300

        self.lg.info(" [*] Open server in container port ,should succeed")
        response = c1_client.bash("mkdir {0} && cd {0}&& echo 'test'>{0}.text ".format(file_name)).get()
        self.assertEqual(response.state, "SUCCESS")
        c1_client.bash("cd %s && python3 -m http.server %i" % (file_name, containerport))

        time.sleep(3)

        self.lg.info("Check that portforward work,should succeed")
        response = c1_client.bash("netstat -nlapt | grep %i" % containerport).get()
        self.assertEqual(response.state, 'SUCCESS')
        url = 'http://{0}:{1}/{2}.text'.format(self.nodeip, hostport, file_name)
        response = urlopen(url)
        html = response.read()
        self.assertIn("test", html.decode('utf-8'))

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
        flist = "https://hub.gig.tech/dina_magdy/initprocess.flist"
        ## flist which have script which print environment varaibles and print stdin
        Environmentvaraible = "MYVAR=%s" % self.rand_str()
        stdin = self.rand_str()
        job_body = {
            'name': 'sh',
            'pwd': '/',
            'args': ["sbin/process_init"],
            "environment": [Environmentvaraible],
            "stdin": stdin
        }
        self.lg.info(" [*] Create container C1 with open port")
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, flist=flist)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        c1_client = self.core0_client.get_container_client(data_c1['name'])

        self.lg.info(' [*] Send post  nodes/{nodeid}/containers/containerid/jobs api request.')
        response = self.containers_api.post_containers_containerid_jobs(self.nodeid, data_c1['name'],
                                                                        job_body)
        self.assertEqual(response.status_code, 202)
        job_id = response.headers['Location'].split('/')[6]
        self.assertTrue(self.core0_client.wait_on_container_job_update(data_c1['name'], job_id, 15, False))

        self.lg.info("check that job created successfully with it's specs.")
        response = c1_client.bash("ls |grep  out.text").get()
        self.assertEqual(response.state, "SUCCESS")
        response = c1_client.bash("cat out.text | grep %s" % stdin).get()
        self.assertEqual(response.state, "SUCCESS", "job didn't get stdin correctly")
        response = c1_client.bash("cat out.text | grep %s" % Environmentvaraible).get()
        self.assertEqual(response.state, "SUCCESS", "job didn't get Env varaible  correctly")

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/892')
    def test017_Create_containers_with_common_vlan(self):
        """ GAT-098

        *Test case for test creation of containers with cmmon vlan  network*

        **Test Scenario:**

        #. Create ovs container .
        #. Create C1 which is binding to vlan1 and vlan2.
        #. Create C2 which is binding to vlan1.
        #. Create C3 which is binding to vlan2.
        #. Check that containers get correct vlan ip, should succeed
        #. Check that C1 can ping C2 and C3 ,should succeed.
        #. Check that C2 can ping C1 and can't ping C3, should succeed.
        #. Check that C3 can ping C1 and can't ping C2,should succeed.

        """
        self.lg.info(" [*] create ovs container")
        self.core0_client.create_ovs_container()
        vlan1_id, vlan2_id = random.sample(range(1, 4096), 2)
        C1_ip_vlan1 = "201.100.2.1"
        C1_ip_vlan2 = "201.100.3.1"
        C2_ip = "201.100.2.2"
        C3_ip = "201.100.3.2"

        nic = [{'type': 'vlan', 'id': vlan1_id, 'config': {'cidr': '%s/24' % C1_ip_vlan1}},
               {'type': 'vlan', 'id': vlan2_id, 'config': {'cidr': '%s/24' % C1_ip_vlan2}}]
        self.lg.info(" [*] Create container C1")
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        self.lg.info("Create C2 which is binding to vlan1.")
        nic = [{'type': 'vlan', 'id': vlan1_id, 'config': {'cidr': '%s/24' % C2_ip}}]
        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

        self.lg.info("Create C3 which is binding to vlan2.")
        nic = [{'type': 'vlan', 'id': vlan2_id, 'config': {'cidr': '%s/24' % C3_ip}}]
        response_c3, data_c3 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c3.status_code, 201)

        self.lg.info("Get three containers client c1_client ,c2_client ansd C3_client.")
        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])
        C3_client = self.core0_client.get_container_client(data_c3['name'])

        self.lg.info("Check that containers get correct vlan ip, should succeed ")
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(c1_client, C1_ip_vlan1))
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(c1_client, C1_ip_vlan2))
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(c2_client, C2_ip))
        self.assertTrue(self.core0_client.check_container_vlan_vxlan_ip(C3_client, C3_ip))

        self.lg.info("Check that C1 can ping C2 and C3 ,should succeed.")
        response = c1_client.bash('ping -w 5 %s' % C2_ip).get()
        self.assertEqual(response.state, "SUCCESS")
        response = c1_client.bash('ping -w 5 %s' % C3_ip).get()
        self.assertEqual(response.state, "SUCCESS")

        self.lg.info("Check that C2 can ping C1 and can't ping C3, should succeed.")
        response = c2_client.bash('ping -w 5 %s' % C1_ip_vlan1).get()
        self.assertEqual(response.state, "SUCCESS")

        response = c2_client.bash('ping -w 5 %s' % C3_ip).get()
        self.assertEqual(response.state, "ERROR")

        self.lg.info("Check that C3 can ping C1 and can't ping C2, should succeed.")
        response = C3_client.bash('ping -w 5 %s' % C1_ip_vlan2).get()
        self.assertEqual(response.state, "SUCCESS")

        response = C3_client.bash('ping -w 5 %s' % C2_ip).get()
        self.assertEqual(response.state, "ERROR")

    def test018_attach_different_nics_to_same_container(self):
        """ GAT-141
        *Check container behaviour with attaching different nics to it*

        **Test Scenario:**

        #. Create container without nic, should succeed
        #. Attach a non existent bridge to the container ,should fail.
        #. Create two bridges (B1 and B2), should succeed.
        #. Attach B1 to the container, should succeed
        #. Attach B2 only to the container, should succeed
        #. Get Container, should find B2 only
        #. Attach Both B1 and B2, should succeed

        """
        self.lg.info('Create container without nic, should succeed')
        self.response, self.data = self.containers_api.post_containers(nodeid=self.nodeid, nics=[])
        self.assertEqual(self.response.status_code, 201, " [*] Can't create new container.")
        cont_name = self.data['name']
        self.created['container'].append(cont_name)

        self.lg.info('Attach a non existent bridge to the container, should fail')
        nics = [{'type': 'bridge', 'id': self.random_string()}]
        try:
            self.response, self.data = self.containers_api.update_container(self.nodeid, cont_name, nics=nics)
        except requests.HTTPError as e:
            self.assertEqual(e.response.status_code, 400)

        self.lg.info('create two bridges (B1 and B2), should succeed')
        response, data_bridge = self.bridges_api.post_nodes_bridges(node_id=self.nodeid)
        B1 = data_bridge['name']
        self.created['bridge'].append(B1)
        response, data_bridge = self.bridges_api.post_nodes_bridges(node_id=self.nodeid)
        B2 = data_bridge['name']
        self.created['bridge'].append(B2)

        self.lg.info('Attach B1 to the container, should succeed')
        nic1 = [{'type': 'bridge', 'id': B1}]
        self.response, self.data = self.containers_api.update_container(self.nodeid, cont_name, nics=nic1)
        self.assertEqual(self.response.status_code, 201)

        self.lg.info('Attach B2 only to the container, should succeed')
        nic2 = [{'type': 'bridge', 'id': B2}]
        self.response, self.data = self.containers_api.update_container(self.nodeid, cont_name, nics=nic2)
        self.assertEqual(self.response.status_code, 201)

        self.lg.info('Get Container, should find B2 only ')
        self.response = self.containers_api.get_containers_containerid(self.nodeid, cont_name)
        d = json.loads(self.response.text.split('\n')[0])
        self.assertEqual(len(d['nics']), 1)
        self.assertEqual(d['nics'][0]['id'], nic2[0]['id'])

        self.lg.info('Attach Both B1 and B2, should succeed')
        nic3 = [{'type': 'bridge', 'id': B1}, {'type': 'bridge', 'id': B2}]
        self.response, self.data = self.containers_api.update_container(self.nodeid, cont_name, nics=nic3)
        d = json.loads(self.response.text.split('\n')[0])
        self.assertEqual(len(d['nics']), 2)
