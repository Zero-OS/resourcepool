import random, time, unittest
from testcases.testcases_base import TestcasesBase
from urllib.request import urlopen
import requests
import json

# @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/892')
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
    
    def test001_create_containers_with_zerotier(self):

        """ GAT-089
        *Test case for create containers with same zerotier network *

        **Test Scenario:**
        #. Create Zerotier network using zerotier api ,should succeed.
        #. Create two containers C1,C2 with same zertoier networkId, should succeed.
        #. Check that two containers get zerotier ip, should succeed.
        #. Make sure that two containers can connect to each other, should succeed.

        """

        Z_Id = self.create_zerotier_network()

        time.sleep(15)

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
        for i in range(5):
            response = c1_client.bash('ping -w3 %s' % c2_zt_ip).get()
            if response.state == "SUCCESS":
                break
            else:
                time.sleep(5)
    
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

    def test002_create_containers_with_vlan_network(self):
        """ GAT-090

        *Test case for test creation of containers with vlan network*

        **Test Scenario:**

        #. Create two containers with same vlan tag, should succeed.
        #. Check that two containers get correct vlan ip, should succeed.
        #. First container C1 ping second container C2 ,should succeed.
        #. Second container C2 ping first container C1 ,should succeed.
        #. Create C3 with different vlan tag , should succeed.
        #. Check if third container (c3) can ping first container (c1), should fail.

        """

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

    def test003_create_containers_with_vxlan_network(self):
        """ GAT-091

        *Test case for test creation of containers with vxlan network*

        **Test Scenario:**

        #. Create two containers with same vxlan tag, should succeed.
        #. Check that two containers get correct vxlan ip, should succeed.
        #. First container C1 ping second container C2 ,should succeed.
        #. Second container C2 ping first container C1 ,should succeed.
        #. Create third container c3 with different vxlan Id,should succeed
        #. Check if third container (c3) can ping first container (c1), should fail.
        """

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

    def test004_create_containers_with_gateway_network_in_config(self):
        """ GAT-092

        *Test case for test creation of containers with gateway in configeration  *

        **Test Scenario:**

        #. Create bridge (B0) with nat true and  with static network mode .
        #. Create container (C1) with (B0) without gateway.
        #. Create container (C2) with (B0) with gateway same ip of bridge.
        #. Check that (C1) can connect to internet, should fail.
        #. Check that (C2) can connect to internet, should succeed.

        """

        self.lg.info('Create bridge with static network and nat true , should succeed')
        response, data_bridge_1 = self.bridges_api.post_nodes_bridges(node_id=self.nodeid, networkMode='dnsmasq', nat=True)
        self.created['bridge'].append(data_bridge_1['name'])
        self.assertEqual(response.status_code, 201, response.content)

        time.sleep(3)

        self.lg.info("Create container (C1) with (B0) without gateway.")
        nics = [{"type": "bridge", "id": data_bridge_1['name'], "status": "up", "name":"test"}]
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        self.lg.info("Create container (C2) with (B0) with gateway same ip of bridge.")
        nics = [{"type": "bridge", "id": data_bridge_1['name'],
                 "config": {"cidr": "192.122.2.3/24", "gateway": data_bridge_1['setting']['cidr'][:-3]},
                 "status": "up"}]

        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nics)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

       
        c1_client = self.core0_client.get_container_client(data_c1['name'])
        c2_client = self.core0_client.get_container_client(data_c2['name'])

        time.sleep(5)

        self.lg.info("Check that C1 can connect to internet, should fail.")
        response = c1_client.bash("ping -w 5  8.8.8.8").get()
        self.assertEqual(response.state, "ERROR", response.stdout)

        self.lg.info("Check that C2 can connect to internet, should fail.")
        response = c2_client.bash("ping -w 5 8.8.8.8").get()
        self.assertEqual(response.state, "SUCCESS", response.stdout)

        self.lg.info("Delete created bridge ")
        self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid, data_bridge_1['name'])

    def test005_create_container_with_dns_in_config(self):
        """ GAT-093

        *Test case for test creation of containers with different network and with dns *

        **Test Scenario:**

        #. Create container (C1) with type default in nic with dns.
        #. Check if values of dns in /etc/resolve.conf ,should fail .
        #. Create container (c2) with vlan and with dns .
        #. Check if values of dns in /etc/resolve.conf ,should succeed .

        """

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

    
    def test006_create_containers_with_ports(self):
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

        self.lg.info("[*] Create rule on port 7070")
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

        time.sleep(5)

        self.lg.info("Check that portforward work,should succeed")
        for i in range(5):
            response = c1_client.bash("netstat -nlapt | grep %i" % containerport).get()
            if response.state == 'SUCCESS':
                break
            time.sleep(5)
        self.assertEqual(response.state, 'SUCCESS')
        url = 'http://{0}:{1}/{2}.text'.format(self.nodeip, hostport, file_name)
        response = urlopen(url)
        html = response.read()
        self.assertIn("test", html.decode('utf-8'))

    @unittest.skip("https://github.com/g8os/resourcepool/issues/297")
    def test007_post_new_job_to_container_with_specs(self):
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

    def test008_Create_containers_with_common_vlan(self):
        """ GAT-098

        *Test case for test creation of containers with cmmon vlan  network*

        **Test Scenario:**

        #. Create C1 which is binding to vlan1 and vlan2.
        #. Create C2 which is binding to vlan1.
        #. Create C3 which is binding to vlan2.
        #. Check that containers get correct vlan ip, should succeed
        #. Check that C1 can ping C2 and C3 ,should succeed.
        #. Check that C2 can ping C1 and can't ping C3, should succeed.
        #. Check that C3 can ping C1 and can't ping C2,should succeed.

        """

        vlan1_id, vlan2_id = random.sample(range(1, 4095), 2)
        C1_ip_vlan1 = "201.100.2.1"
        C1_ip_vlan2 = "201.100.3.1"
        C2_ip = "201.100.2.2"
        C3_ip = "201.100.3.2"

        nic = [{'type': 'vlan', 'id': str(vlan1_id), 'config': {'cidr': '%s/24' % C1_ip_vlan1}},
               {'type': 'vlan', 'id': str(vlan2_id), 'config': {'cidr': '%s/24' % C1_ip_vlan2}}]
        self.lg.info(" [*] Create container C1")
        response_c1, data_c1 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c1.status_code, 201)
        self.created['container'].append(data_c1['name'])

        self.lg.info("Create C2 which is binding to vlan1.")
        nic = [{'type': 'vlan', 'id': str(vlan1_id), 'config': {'cidr': '%s/24' % C2_ip}}]
        response_c2, data_c2 = self.containers_api.post_containers(nodeid=self.nodeid, nics=nic)
        self.assertEqual(response_c2.status_code, 201)
        self.created['container'].append(data_c2['name'])

        self.lg.info("Create C3 which is binding to vlan2.")
        nic = [{'type': 'vlan', 'id': str(vlan2_id), 'config': {'cidr': '%s/24' % C3_ip}}]
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

    def test009_Create_containers_with_different_nics(self):
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
        self.containers_api.update_container(self.nodeid, cont_name, nics=nic3)
        self.response = self.containers_api.get_containers_containerid(self.nodeid, cont_name)
        d = json.loads(self.response.text.split('\n')[0])
        self.assertEqual(len(d['nics']), 2)
