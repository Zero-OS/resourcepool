import random, time
from testcases.testcases_base import TestcasesBase
import unittest

class TestGatewayAPICreation(TestcasesBase):
    def setUp(self):
        super().setUp()
        self.core0_client.create_ovs_container()
        self.core0_client.timeout = 30
        self.flist = 'https://hub.gig.tech/gig-official-apps/ubuntu1604.flist'
        self.container_body = {"name": self.rand_str(),
                               "hostname": self.rand_str(),
                               "flist": self.flist}

    def tearDown(self):
        self.lg.info(' [*] Delete all created {} gateways'.format(self.nodeid))
        attributes = self.__dict__.keys()
        if 'data' in attributes:
            if self.data:
                self.gateways_api.delete_nodes_gateway(self.nodeid, self.data['name'])

        self.lg.info(' [*] TearDown:delete all created container ')
        if 'container_data' in attributes:
            if self.container_data:
                self.containers_api.delete_containers_containerid(self.nodeid,
                                                                  self.container_data['name'])

        self.lg.info(' [*] TearDown:delete all created bridges ')
        if 'bridge_data' in attributes:
            if self.bridge_data:
                self.bridges_api.delete_nodes_bridges_bridgeid(self.nodeid,
                                                               self.bridge_data['name'])
        super().tearDown()

    def create_vm(self, nics):
        response = self.storageclusters_api.get_storageclusters()
        self.assertEqual(response.status_code, 200)
        storageclusters = response.json()
        if storageclusters:
            storagecluster = storageclusters[-1]
        else:
            free_disks = self.core0_client.getFreeDisks()
            if free_disks == []:
                self.skipTest(' [*] no free disks to create storagecluster.')
            self.lg.info(' [*] Deploy new storage cluster (SC0).')
            response, data = self.storageclusters_api.post_storageclusters(node_id=self.nodeid)
            self.assertEqual(response.status_code, 201)
            storagecluster = data['label']

        self.lg.info(' [*] Create new vdisk.')
        response, data = self.vdisks_api.post_vdisks(storagecluster=storagecluster, size=15, blocksize=4096, type='boot')
        boot_disk = data['id']

        self.lg.info(' [*] Create virtual machine (VM0) on node (N0)')
        disks = [{"vdiskid": boot_disk, "maxIOps": 2000}]
        response, data = self.vms_api.post_nodes_vms(node_id=self.nodeid, memory=1024, cpu=1, nics=nics, disks=disks)
        self.assertEqual(response.status_code, 201)
        return data

    def test001_create_gateway_with_xlan_xlan_container(self):
        """ GAT-123
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway with Xlan and Xlan as nics on node (N0), should succeed.
        #. Bind a new container to Xlan(1).
        #. Bind a new container to Xlan(2).
        #. Make sure that those two containers can ping each others.
        """
        self.lg.info(' [*] Create gateway with xlan as nics on node (N0), should succeed')
        nics_type = [{
            'type': random.choice(['vlan', 'vxlan']),
            'gateway': True,
            'dhcp': False,
            'bridge_name': '',
            'zerotierbridge': False

        },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': False,
                'bridge_name': '',
                'zerotierbridge': ''

            },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': False,
                'bridge_name': '',
                'zerotierbridge': ''

            }
        ]

        nics = self.get_gateway_nic(nics_types=nics_type)
        self.response, self.data = self.gateways_api.post_nodes_gateway(self.nodeid, nics=nics)

        self.assertEqual(self.response.status_code, 201)

        self.lg.info(' [*] Bind a new container to vlan(1)')
        nics_container = [{'type': nics[1]['type'],
                           'id': nics[1]['id'],
                           'config': {'dhcp': False,
                                      'gateway': nics[1]['config']['cidr'][:-3],
                                      'cidr': nics[1]['config']['cidr'][:-4] + '10/24'}
                           }]
        uid_1 = self.core0_client.client.container.create(self.flist, nics=nics_container).get()
        container_1 = self.core0_client.client.container.client(int(uid_1))

        self.lg.info(' [*] Bind a new container to vlan(2)')
        nics_container = [{'type': nics[2]['type'],
                           'id': nics[2]['id'],
                           'config': {'dhcp': False,
                                      'gateway': nics[2]['config']['cidr'][:-3],
                                      'cidr': nics[2]['config']['cidr'][:-4] + '10/24'}
                           }]

        uid = self.core0_client.client.container.create(self.flist, nics=nics_container).get()
        container_2 = self.core0_client.client.container.client(int(uid))

        time.sleep(5)

        self.lg.info(' [*] Make sure that those two containers can ping each others')
        response = container_1.bash('ping -w5 %s' % nics[2]['config']['cidr'][:-4] + '10').get()
        self.assertEqual(response.state, 'SUCCESS')
        response = container_2.bash('ping -w5 %s' % nics[1]['config']['cidr'][:-4] + '10').get()
        self.assertEqual(response.state, 'SUCCESS')

        self.core0_client.client.container.terminate(int(uid_1))
        self.core0_client.client.container.terminate(int(uid))

    @unittest.skip('ssh to vm issue')
    def test003_create_gateway_with_xlan_xlan_vm(self):
        """ GAT-125
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway with vlan and vlan as nics on node (N0), should succeed.
        #. Bind a new vm to vlan(1).
        #. Bind a new vm to vlan(2).
        #. Make sure that those two containers can ping each others.
        """
        nics_type = [{
            'type':'bridge',
            'gateway': True,
            'dhcp': False,
            'bridge_name': '',
            'zerotierbridge': False

        },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': ''

            },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': ''

            }
        ]

        nics = self.get_gateway_nic(nics_types=nics_type)
        vm1_mac_addr = nics[1]['dhcpserver']['hosts'][1]['macaddress']
        vm1_ip_addr = nics[1]['dhcpserver']['hosts'][1]['ipaddress']
        vm2_mac_addr = nics[2]['dhcpserver']['hosts'][1]['macaddress']
        vm2_ip_addr = nics[2]['dhcpserver']['hosts'][1]['ipaddress']
        test_container_mac_addr = nics[1]['dhcpserver']['hosts'][0]['macaddress']
        nics[2]['dhcpserver']['hosts'][0]['macaddress'] = test_container_mac_addr

        ## set cloudinit
        cloudinit = {"chpasswd": {"expire": false}, 
        "ssh_pwauth":true, "users": 
        [{"plain_text_passwd": "GB389z2wZ", "lock-passwd": false,"name": "gig", "shell": "/bin/bash", "sudo": "ALL=(ALL) ALL"}]}

        self.response, self.data = self.gateways_api.post_nodes_gateway(self.nodeid, nics=nics)
        self.assertEqual(self.response.status_code, 201)

        nics = [{'id': nics[1]['id'], 'type': nics[1]['type'], 'macaddress': vm1_mac_addr}]
        self.create_vm(nics=nics)

        nics = [{'id': nics[2]['id'], 'type': nics[2]['type'], 'macaddress': vm2_mac_addr}]
        self.create_vm(nics=nics)

        self.lg.info(' [*] create test container')
        nics = [{'type': nics[1]['type'], 'id': nics[1]['id'], 'config': {'dhcp': True}, 'hwaddr': test_container_mac_addr},
                {'type': nics[2]['type'], 'id': nics[2]['id'], 'config': {'dhcp': True}, 'hwaddr': test_container_mac_addr}]

        uid = self.core0_client.client.container.create(self.flist, nics=nics).get()
        test_container = self.core0_client.client.container.client(uid)

        time.sleep(60)

        response = test_container.bash(
            'sshpass -p rooter ssh gig@%s -oStrictHostKeyChecking=no ping %s' % (vm1_ip_addr, vm2_ip_addr)).get()
        self.assertEqual(response.state, 'SUCCESS', response.stderr)

        response = test_container.bash(
            'sshpass -p rooter ssh gig@%s -oStrictHostKeyChecking=no ping %s' % (vm2_ip_addr, vm1_ip_addr)).get()
        self.assertEqual(response.state, 'SUCCESS', response.stderr)


    def test005_create_gateway_with_bridge_xlan_container(self):
        """ GAT-127
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway with bridge and vxlan as nics on node (N0), should succeed.
        #. Bind a new container to vlan(1).
        #. Verify that this container has public access.
        """
        bridge_name = 'b' + self.random_string()

        nics_type = [{
            'type': 'bridge',
            'gateway': True,
            'dhcp': False,
            'bridge_name': bridge_name,
            'zerotierbridge': ''

        },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': ''

            }
        ]
        
        nics = self.get_gateway_nic(nics_types=nics_type)

        self.lg.info(' [*] Create bridge (B1) on node (N0), should succeed with 201')
        setting = {"cidr": nics[0]['config']['gateway'] + '/24'}
        response, self.bridge_data = self.bridges_api.post_nodes_bridges(self.nodeid, name=bridge_name, networkMode='static', nat=True, setting=setting)
        self.assertEqual(response.status_code, 201, response.content)
        
        self.response, self.data = self.gateways_api.post_nodes_gateway(self.nodeid, nics=nics)
        self.assertEqual(self.response.status_code, 201)

        self.lg.info(' [*] Create container')
        nics_container = [{"type": nics[1]['type'],
                           "id": nics[1]['id'],
                           "hwaddr": nics[1]['dhcpserver']['hosts'][0]['macaddress'],
                           "config": {"dhcp": True}}]

        response, self.container_data = self.containers_api.post_containers(self.nodeid, nics=nics_container)
        self.assertEqual(response.status_code, 201, " [*] Can't create container.")
        container = self.core0_client.get_container_client(self.container_data['name'])
        self.assertTrue(container)

        time.sleep(5)

        response = container.bash('ping -w3 8.8.8.8').get()
        self.assertEqual(response.state, 'SUCCESS')
        self.assertNotIn("unreachable", response.stdout)

    @unittest.skip('ssh to vm issue')
    def test007_create_gateway_with_bridge_xlan_vm(self):
        """ GAT-129
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway with bridge and vlan as nics on node (N0), should succeed.
        #. Bind a new vm to vlan(1).
        #. Verify that this vm has public access.
        """
        self.lg.info(' [*] Create bridge (B1) on node (N0), should succeed with 201')
        response, self.bridge_data = self.bridges_api.post_nodes_bridges(self.nodeid, networkMode='static', nat=True)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        nics_type = [{
            'type': 'bridge',
            'gateway': True,
            'dhcp': False,
            'bridge_name': self.bridge_data['name'],
            'zerotierbridge': ''

        },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': ''

            }
        ]

        nics = self.get_gateway_nic(nics_types=nics_type)
        self.response, self.data = self.gateways_api.post_nodes_gateway(self.nodeid, nics=nics)
        self.assertEqual(self.response.status_code, 201)

        vm1_mac_addr = nics_type[1]['dhcpserver']['hosts'][0]['macaddress']
        vm1_ip_addr = nics_type[1]['dhcpserver']['hosts'][0]['ipaddress']
        test_container_mac_addr = nics_type[1]['dhcpserver']['hosts'][1]['macaddress']

        nics = [{'id': nics[1]['id'], 'type': nics[1]['type'], 'macaddress': vm1_mac_addr}]
        self.create_vm(nics=nics)

        self.lg.info(' [*] create test container')
        nics = [{'type': nics[1]['type'], 'id': nics[1]['id'], 'config': {'dhcp': True}, 'hwaddr': test_container_mac_addr}]
        uid = self.core0_client.client.container.create(self.flist, nics=nics).get()
        test_container = self.core0_client.client.container.client(uid)

        test_container.bash('apt install ssh -y; apt install sshpass -y')
        time.sleep(60)

        response = test_container.bash('ssh gig@%s -oStrictHostKeyChecking=no ping -w3 8.8.8.8' % vm1_ip_addr).get()
        self.assertEqual(response.state, 'SUCCESS')
        self.core0_client.client.container.terminate(int(uid))

    def test009_create_gateway_dhcpserver(self):
        """ GAT-131
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway with bridge and xlan as nics on node (N0), should succeed.
        #. Specify a dhcpserver for container and vm in this GW
        #. Create a container and vm to match the dhcpserver specs
        #. Verify that container and vm ips are matching with the dhcpserver specs.
        """
        self.lg.info(' [*] Create bridge (B1) on node (N0), should succeed with 201')
        response, self.bridge_data = self.bridges_api.post_nodes_bridges(self.nodeid, networkMode='static', nat=True)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        nics_type = [{
            'type': 'bridge',
            'gateway': True,
            'dhcp': False,
            'bridge_name': self.bridge_data['name'],
            'zerotierbridge': ''

        },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': ''

            }
        ]
        nics = self.get_gateway_nic(nics_types=nics_type)
        self.response, self.data = self.gateways_api.post_nodes_gateway(node_id=self.nodeid, nics=nics)
        self.assertEqual(self.response.status_code, 201, response.content)

        nics_container = [{
            'type': nics[1]['type'],
            'name': 'test',
            'id': nics[1]['id'],
            'hwaddr': nics[1]['dhcpserver']['hosts'][0]['macaddress'],
            'config': {'dhcp': True}
        }]

        uid = self.core0_client.client.container.create(self.flist, nics=nics_container).get()
        
        time.sleep(5)

        container_1 = self.core0_client.client.container.client(int(uid))
        container_1_nics = container_1.info.nic()
        interface = [x for x in container_1_nics if x['name'] == 'test']
        self.assertNotEqual(interface, [])
        self.assertIn(nics[1]['dhcpserver']['hosts'][0]['ipaddress'], [x['addr'][:-3] for x in interface[0]['addrs']])
        self.assertEqual(nics[1]['dhcpserver']['hosts'][0]['macaddress'], interface[0]['hardwareaddr'])
        self.core0_client.client.container.terminate(int(uid))

    @unittest.skip('https://github.com/zero-os/0-orchestrator/issues/1102')
    def test010_create_gateway_httpproxy(self):
        """ GAT-132
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway with bridge and vlan as nics and httpproxy with two containers on node (N0), should succeed.
        #. Create two containers to for test the httpproxy's configuration
        #. Verify that the httprxoy's configuration is working right
        """
        self.lg.info(' [*] Create bridge (B1) on node (N0), should succeed with 201')
        response, self.bridge_data = self.bridges_api.post_nodes_bridges(self.nodeid, networkMode='static', nat=True)
        self.assertEqual(response.status_code, 201, response.content)
        time.sleep(3)

        nics_type = [{
            'type': 'bridge',
            'gateway': True,
            'dhcp': False,
            'bridge_name': self.bridge_data['name'],
            'zerotierbridge': ''

        },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': ''

            }
        ]
        nics_data = self.get_gateway_nic(nics_types=nics_type)
        httpproxies = [
            {
                "host": "container1",
                "destinations": ['http://{}:1000'.format(nics_data[1]['config']['cidr'][:-4] + '10/24')],
                "types": ['http', 'https']
            },
            {
                "host": "container2",
                "destinations": ['http://{}:2000'.format(nics_data[1]['config']['cidr'][:-4] + '20/24')],
                "types": ['http', 'https']
            }
        ]

        self.response, self.data = self.gateways_api.post_nodes_gateway(node_id=self.nodeid, nics=nics_data, httpproxies=httpproxies)
        self.assertEqual(response.status_code, 201, response.content)

        nics = [{'type': nics_type[1]['type'],
                 'id': nics_data[1]['id'],
                 'config': {'dhcp': False,
                            'gateway': nics_data[1]['config']['cidr'][:-3],
                            'cidr': nics_data[1]['config']['cidr'][:-4] + '10/24'}}]
        uid_1 = self.core0_client.client.container.create(self.flist, nics=nics).get()
        container_1 = self.core0_client.client.container.client(int(uid_1))

        nics = [{'type': nics_type[1]['type'],
                 'id': nics_data[1]['id'],
                 'config': {'dhcp': False,
                            'gateway': nics_data[1]['config']['cidr'][:-3],
                            'cidr': nics_data[1]['config']['cidr'][:-4] + '20/24'}}]
        uid = self.core0_client.client.container.create(self.flist, nics=nics).get()
        container_2 = self.core0_client.client.container.client(int(uid))

        self.lg.info('Make sure that those two containers can ping each others')
        container_1.bash('python3 -m http.server 1000')
        container_2.bash('python3 -m http.server 2000')

        time.sleep(2)

        response = container_1.bash(
            'python3 -c "from urllib.request import urlopen; urlopen(\'{}\')"'.format('http://container2')).get()
        self.assertEqual(response.state, 'SUCCESS')

        response = container_2.bash(
            'python3 -c "from urllib.request import urlopen; urlopen(\'{}\')"'.format('http://container1')).get()
        self.assertEqual(response.state, 'SUCCESS')
        self.core0_client.client.container.terminate(int(uid_1))
        self.core0_client.client.container.terminate(int(uid))

    def test011_create_gateway_portforwards(self):
        """ GAT-133
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create bridge(B0) , should succeed.
        #. Create gateway with bridge and vlan as nics should succeed.
        #. Set a portforward form srcip:80 to destination:80
        #. Create one container as a destination host
        #. Start any service in this container
        #. Using core0_client try to request this service and make sure that u can reach the container

        """
        
        bridge_name = 'b' + self.random_string()

        self.lg.info(" [*] Create gateway with bridge and vlan as nics should succeed.")
        nics_type = [{
            'type': 'bridge',
            'gateway': True,
            'dhcp': False,
            'bridge_name': bridge_name,
            'zerotierbridge': ''

        },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': ''

            }
        ]

        nics = self.get_gateway_nic(nics_types=nics_type)

        self.lg.info(' [*] Create bridge (B1) on node (N0), should succeed with 201')
        setting = {"cidr": nics[0]['config']['gateway'] + '/24'}
        response, self.bridge_data = self.bridges_api.post_nodes_bridges(self.nodeid, name=bridge_name, networkMode='static', nat=True, setting=setting)
        self.assertEqual(response.status_code, 201, response.content)

        portforwards = [
            {
                "srcport": 5000,
                "srcip": nics[0]['config']['cidr'][:-3],
                "dstport": 5000,
                "dstip": nics[1]['dhcpserver']['hosts'][0]['ipaddress'],
                "protocols": [
                    "tcp"
                ]
            }
        ]

        self.lg.info("[*] Create rule on port 80")
        try:
            self.core0_client.client.nft.open_port(5000)
        except:
            pass

        self.response, self.data = self.gateways_api.post_nodes_gateway(node_id=self.nodeid, nics=nics, portforwards=portforwards)
        self.assertEqual(self.response.status_code, 201, response.content)

        self.lg.info(' [*] Create container')
        nics_container = [{"type": nics[1]['type'],
                           "id": nics[1]['id'],
                           "hwaddr": nics[1]['dhcpserver']['hosts'][0]['macaddress'],
                           "config": {"dhcp": True}}]

        response, self.container_data = self.containers_api.post_containers(self.nodeid, nics=nics_container)
        self.assertEqual(response.status_code, 201, " [*] Can't create container.")
        container = self.core0_client.get_container_client(self.container_data['name'])
        self.assertTrue(container)

        file_name = self.random_string()

        self.lg.info(" [*] Start any service in this container")
        response = container.bash("echo test > {}.txt".format(file_name)).get()
        self.assertEqual(response.state, "SUCCESS", response.stderr)

        container.bash("python3 -m http.server 5000")
        
        time.sleep(5)

        url = 'http://{}:5000/{}.txt'.format(nics[0]['config']['cidr'][:-3], file_name)

        response = self.core0_client.client.bash('wget %s' % url).get()
        self.assertEqual(response.state, "SUCCESS", response.stderr)

        response = self.core0_client.client.bash('ls | grep {}.txt'.format(file_name)).get()
        self.assertEqual(response.state, "SUCCESS", response.stderr)

    def test012_create_two_gateways_zerotierbridge(self):
        """ GAT-134
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create bridge(B0) with true nat, should succeed.
        #. Create zerotier network.
        #. Create two Gws (Gw1)(Gw2) and link them with zerotier bridge.
        #. Create (C1),(C2) containers for each Gw .
        #. Verify that each created 'GW containers' hosts can reach each others.

        """
        
        self.lg.info(" [*] Create zerotier network.")
        nwid = self.create_zerotier_network(default_config=False)

        bridge_name = self.random_string()

        self.lg.info(" [*] Create two Gws and link them with zerotier bridge.")
        nics_type = [
            {
                'type': 'bridge',
                'gateway': True,
                'dhcp': False,
                'bridge_name': bridge_name,
                'zerotierbridge': False
            },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': nwid
            }
        ]

        nics = self.get_gateway_nic(nics_types=nics_type)
        c1_ip = nics[1]["dhcpserver"]["hosts"][0]["ipaddress"]

        self.lg.info(' [*] Create bridge (B0) on node (N0), should succeed with 201')
        setting = {"cidr": nics[0]['config']['gateway'] + '/24'}
        response, self.bridge_data = self.bridges_api.post_nodes_bridges(self.nodeid, name=bridge_name, networkMode='static', nat=True, setting=setting)
        self.assertEqual(response.status_code, 201, response.content)

        self.response, self.data = self.gateways_api.post_nodes_gateway(node_id=self.nodeid, nics=nics)
        self.assertEqual(self.response.status_code, 201, self.response.content)

        self.lg.info(" [*] create (c1) containers for each Gw. ")
        c1_nics = [{'type': nics[1]['type'],
                    'id': nics[1]['id'],
                    "hwaddr": nics[1]["dhcpserver"]["hosts"][0]["macaddress"],
                    'config': {"dhcp": True}}]
        response, self.container_data = self.containers_api.post_containers(nodeid=self.nodeid, nics=c1_nics)

        self.assertEqual(response.status_code, 201)
        c1_client = self.core0_client.get_container_client(self.container_data['name'])
        self.assertTrue(c1_client)

        bridge_name_2 = self.random_string()

        nics_type = [
            {
                'type': 'bridge',
                'gateway': True,
                'dhcp': False,
                'bridge_name': bridge_name_2,
                'zerotierbridge': False
            },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': nwid

            }
        ]

        nics_2 = self.get_gateway_nic(nics_types=nics_type)
        nics_2[1]['config'] = nics[1]['config']
        nics_2[1]['dhcpserver'] = nics[1]['dhcpserver']

        c2_ip = nics_2[1]["dhcpserver"]["hosts"][1]["ipaddress"]

        self.lg.info(' [*] Create bridge (B0) on node (N0), should succeed with 201')
        setting = {"cidr": nics_2[0]['config']['gateway'] + '/24'}
        response, self.bridge_data = self.bridges_api.post_nodes_bridges(self.nodeid, name=bridge_name_2, networkMode='static', nat=True, setting=setting)
        self.assertEqual(response.status_code, 201, response.content)

        self.response, self.data = self.gateways_api.post_nodes_gateway(node_id=self.nodeid, nics=nics_2)
        self.assertEqual(self.response.status_code, 201, self.response.content)

        self.lg.info(" [*] create (c2) containers for each Gw. ")
        c2_nics = [{'type': nics[1]['type'],
                    'id': nics[1]['id'],
                    "hwaddr": nics[1]["dhcpserver"]["hosts"][1]["macaddress"],
                    'config': {"dhcp": True}}]

        response, self.container_data = self.containers_api.post_containers(nodeid=self.nodeid, nics=c2_nics)

        self.assertEqual(response.status_code, 201)
        c2_client = self.core0_client.get_container_client(self.container_data['name'])
        self.assertTrue(c2_client)

        response = c1_client.bash('ping -c 5 %s' % c2_ip).get()
        self.assertEqual(response.state, 'SUCCESS')
        self.assertNotIn("unreachable", response.stdout)

        response = c2_client.bash('ping -c 5 %s' % c1_ip).get()
        self.assertEqual(response.state, 'SUCCESS')
        self.assertNotIn("unreachable", response.stdout)


class TestGatewayAPIUpdate(TestcasesBase):
    def setUp(self):
        super().setUp()
        nics_type = [
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': True,
                'dhcp': False,
                'bridge_name': '',
                'zerotierbridge': False
            },
            {
                'type': random.choice(['vlan', 'vxlan']),
                'gateway': False,
                'dhcp': True,
                'bridge_name': '',
                'zerotierbridge': False

            }
        ]
        self.nics = self.get_gateway_nic(nics_types=nics_type)
        self.core0_client.create_ovs_container()
        self.response, self.data = self.gateways_api.post_nodes_gateway(self.nodeid, nics=self.nics)
        self.assertEqual(self.response.status_code, 201)
        self.gw_name = self.data['name']
        self.gw_domain = self.data['domain']

    def tearDown(self):
        self.lg.info(' [*] Delete all node {} gateways'.format(self.nodeid))
        if 'data' in self.__dict__.keys():
            self.gateways_api.delete_nodes_gateway(self.nodeid, self.gw_name)
        super().tearDown()

    def test001_list_gateways(self):
        """ GAT-098
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway (GW0) on node (N0), should succeed.
        #. List all node (N0) gateways, (GW0) should be listed.
        """
        self.lg.info(' [*] List node (N0) gateways, (GW0) should be listed')
        response = self.gateways_api.list_nodes_gateways(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.gw_name, [x['name'] for x in response.json()])

    def test002_get_gateway_info(self):
        """ GAT-099
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway (GW0) on node (N0), should succeed.
        #. Get gateway (GW0) info, should succeed.
        """
        response = self.gateways_api.get_nodes_gateway(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)

    def test003_delete_gateway(self):
        """ GAT-100
        **Test Scenario:**

        #. Get random node (N0), should succeed.
        #. Create gateway (GW0) on node (N0), should succeed.
        #. Delete gateway (GW0), should succeed.
        #. List node (N0) gateways, (GW0) should not be listed.
        """

        self.lg.info(' [*] Delete gateway (GW0), should succeed')
        response = self.gateways_api.delete_nodes_gateway(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List node (N0) gateways, (GW0) should not be listed')
        response = self.gateways_api.list_nodes_gateways(self.nodeid)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.gw_name, [x['name'] for x in response.json()])

    def test004_stop_gw(self):
        """ GAT-135
        **Test Scenario:**

        #. Stop the running gatway
        #. Verify its status
        """
        response = self.containers_api.get_containers(nodeid=self.nodeid)
        for container in response.json():
            if self.gw_name == container['name']:
                self.assertEqual(container['status'], 'running')

        response = self.gateways_api.post_nodes_gateway_stop(nodeid=self.nodeid, gwname=self.gw_name)
        self.assertEqual(response.status_code, 204, response.content)

        response = self.containers_api.get_containers(nodeid=self.nodeid)
        for container in response.json():
            if self.gw_name == container['name']:
                self.assertEqual(container['status'], 'halted')

        response = self.gateways_api.post_nodes_gateway_start(nodeid=self.nodeid, gwname=self.gw_name)
        self.assertEqual(response.status_code, 204, response.content)

    def test005_start_gw(self):
        """ GAT-136
        **Test Scenario:**

        #. Stop the running gateway and make sure that its status has been changed
        #. Start the gateway
        #. Verify its status
        """
        response = self.gateways_api.post_nodes_gateway_stop(nodeid=self.nodeid, gwname=self.gw_name)
        self.assertEqual(response.status_code, 204, response.content)

        response = self.containers_api.get_containers(nodeid=self.nodeid)
        for container in response.json():
            if self.gw_name == container['name']:
                self.assertEqual(container['status'], 'halted')

        response = self.gateways_api.post_nodes_gateway_start(nodeid=self.nodeid, gwname=self.gw_name)
        self.assertEqual(response.status_code, 204, response.content)

        response = self.containers_api.get_containers(nodeid=self.nodeid)
        for container in response.json():
            if self.gw_name == container['name']:
                self.assertEqual(container['status'], 'running')

    def test006_update_gw_nics_config(self):
        """ GAT-137
        **Test Scenario:**

        #. Use put method to update the nics config for the gw
        #. List the gw and make sure that its nics config have been updated
        """
        nics = list(self.nics)
        nics[0]['config']['cidr'] = "192.168.10.10/24"
        nics[0]['config']['gateway'] = "192.168.10.1"
        nics[1]['config']['cidr'] = "192.168.20.2/24"
        del nics[1]['dhcpserver']
        data = dict(self.data)
        data['nics'] = nics

        self.lg.info(' [*] Use put method to update the nics config for the gw')
        response = self.gateways_api.update_nodes_gateway(self.nodeid, self.gw_name, data)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List the gw and make sure that its nics config have been updated')
        response = self.gateways_api.get_nodes_gateway(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(nics, response.json()['nics'])

    def test007_update_gw_portforwards_config(self):
        """ GAT-138
        **Test Scenario:**

        #. Use put method to update the portforwards config for the gw
        #. List the gw and make sure that its portforwards config have been updated
        """
        self.data['portforwards'] = [
            {
                "protocols": ['udp', 'tcp'],
                "srcport": random.randint(100, 1000),
                "srcip": "192.168.1.1",
                "dstport": random.randint(100, 1000),
                "dstip": "192.168.2.100"
            }
        ]

        del self.data['name']

        self.lg.info(' [*] Use put method to update the portforwards config for the gw')
        response = self.gateways_api.update_nodes_gateway(self.nodeid, self.gw_name, self.data)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List the gw and make sure that its portforwards config have been updated')
        response = self.gateways_api.get_nodes_gateway(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.data['portforwards'], response.json()['portforwards'])

    def test008_update_gw_dhcpserver_config(self):
        """ GAT-139
        **Test Scenario:**

        #. Use put method to update the dhcpserver config for the gw
        #. List the gw and make sure that its dhcpserver config have been updated
        """
        self.data['nics'][1]['dhcpserver'] = {
            "nameservers": ["8.8.8.8"],
            "hosts": [
                {
                    "macaddress": self.randomMAC(),
                    "hostname": self.random_string(),
                    "ipaddress": self.data['nics'][1]['config']['cidr'][:-4] + '10'
                }
            ]
        }

        del self.data['name']

        self.lg.info(' [*] Use put method to update the dhcpserver config for the gw')
        response = self.gateways_api.update_nodes_gateway(self.nodeid, self.gw_name, self.data)
        self.assertEqual(response.status_code, 204, response.content)

        self.lg.info(' [*] List the gw and make sure that its dhcpserver config have been updated')
        response = self.gateways_api.get_nodes_gateway(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.data['nics'][1]['dhcpserver'], response.json()['nics'][1]['dhcpserver'])

    def test009_update_gw_httpproxies_config(self):
        """ GAT-140
        **Test Scenario:**

        #. Use put method to update the dhcpserver config for the gw
        #. List the gw and make sure that its httpproxies config have been updated
        """
        self.data['httpproxies'] = [
            {
                "host": self.random_string(),
                "destinations": ["192.168.200.10:1101"],
                "types": ['https', 'http']
            }
        ]

        del self.data['name']

        self.lg.info(' [*] Use put method to update the dhcpserver config for the gw')
        response = self.gateways_api.update_nodes_gateway(self.nodeid, self.gw_name, self.data)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List the gw and make sure that its dhcpserver config have been updated')
        response = self.gateways_api.get_nodes_gateway(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.data['httpproxies'], response.json()['httpproxies'])

    def test010_create_list_portforward(self):
        """ GAT-114
        **Test Scenario:**

        #. Create new portforward table using firewall/forwards api
        #. Verify it is working right
        """
        body = {
            "protocols": ['udp', 'tcp'],
            "srcport": random.randint(1, 2000),
            "srcip": "192.168.1.1",
            "dstport": random.randint(1, 2000),
            "dstip": "192.168.2.5"
        }

        self.lg.info(' [*] Create new portforward table using firewall/forwards api')
        response = self.gateways_api.post_nodes_gateway_forwards(self.nodeid, self.gw_name, body)
        self.assertEqual(response.status_code, 201, response.content)

        self.lg.info(' [*] Verify it is working right')
        response = self.gateways_api.list_nodes_gateway_forwards(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)
        self.assertIn(body, response.json())

    def test012_delete_portforward(self):
        """ GAT-115
        **Test Scenario:**

        #. Create new portforward table using firewall/forwards api
        #. List portfowards table
        #. Delete this portforward config
        #. List portforwards and verify that it has been deleted
        """
        body = {
            "protocols": ['udp', 'tcp'],
            "srcport": random.randint(1, 2000),
            "srcip": "192.168.1.1",
            "dstport": random.randint(1, 2000),
            "dstip": "192.168.2.5"
        }

        self.lg.info(' [*] Create new portforward table using firewall/forwards api')
        response = self.gateways_api.post_nodes_gateway_forwards(self.nodeid, self.gw_name, body)
        self.assertEqual(response.status_code, 201, response.content)

        self.lg.info(' [*] List portfowards table')
        response = self.gateways_api.list_nodes_gateway_forwards(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)
        self.assertIn(body, response.json())

        self.lg.info(' [*] Delete this portforward config')
        forwardid = '{}:{}'.format(body['srcip'], body['srcport'])
        response = self.gateways_api.delete_nodes_gateway_forward(self.nodeid, self.gw_name, forwardid)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List portfowards table')
        response = self.gateways_api.list_nodes_gateway_forwards(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(body, response.json())

    def test013_add_dhcp_host(self):
        """ GAT-116
        **Test Scenario:**
        #. Add new dhcp host to an interface
        #. List dhcp hosts
        #. Verify that is the list has the config
        """
        self.lg.info(' [*] Add new dhcp host to an interface')
        interface = [x for x in self.nics if x.get('dhcpserver')][0]['name']
        hostname = self.random_string()
        macaddress = self.randomMAC()
        ipaddress = '192.168.2.3'
        body = {
            "hostname": hostname,
            "macaddress": macaddress,
            "ipaddress": ipaddress
        }

        response = self.gateways_api.post_nodes_gateway_dhcp_host(self.nodeid, self.gw_name, interface, body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List dhcp hosts')
        response = self.gateways_api.list_nodes_gateway_dhcp_hosts(self.nodeid, self.gw_name, interface)
        self.assertEqual(response.status_code, 200)

        self.lg.info(' [*] Verify that is the list has the config')
        dhcp_host = [x for x in response.json() if x['hostname'] == hostname]
        self.assertNotEqual(dhcp_host, [])
        for key in body.keys():
            self.assertTrue(body[key], dhcp_host[0][key])

    def test014_delete_dhcp_host(self):
        """ GAT-117
        **Test Scenario:**
        #. Add new dhcp host to an interface
        #. List dhcp hosts
        #. Delete one host form the dhcp
        #. List dhcp hosts
        #. Verify that the dhcp has been updated
        """
        self.lg.info(' [*] Add new dhcp host to an interface')
        interface = [x for x in self.nics if x.get('dhcpserver')][0]['name']
        hostname = self.random_string()
        macaddress = self.randomMAC()
        ipaddress = '192.168.2.3'
        body = {
            "hostname": hostname,
            "macaddress": macaddress,
            "ipaddress": ipaddress
        }

        response = self.gateways_api.post_nodes_gateway_dhcp_host(self.nodeid, self.gw_name, interface, body)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*]  Delete one host form the dhcp')
        response = self.gateways_api.delete_nodes_gateway_dhcp_host(self.nodeid, self.gw_name, interface, macaddress)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List dhcp hosts')
        response = self.gateways_api.list_nodes_gateway_dhcp_hosts(self.nodeid, self.gw_name, interface)
        self.assertEqual(response.status_code, 200)

        self.lg.info(' [*] Verify that the dhcp has been updated')
        dhcp_host = [x for x in response.json() if x['hostname'] == hostname]
        self.assertEqual(dhcp_host, [])

    def test015_create_new_httpproxy(self):
        """ GAT-118
        **Test Scenario:**
        #. Create new httpproxy
        #. List httpproxy config
        #. Verify that is the list has the config
        """

        self.lg.info(' [*] Add new httpproxy host to an interface')
        body = {
            "host": self.random_string(),
            "destinations": ['http://192.168.2.200:5000'],
            "types": ['http', 'https']
        }

        response = self.gateways_api.post_nodes_gateway_httpproxy(self.nodeid, self.gw_name, body)
        self.assertEqual(response.status_code, 201)

        self.lg.info(' [*] List dhcp httpproxy')
        response = self.gateways_api.list_nodes_gateway_httpproxies(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)

        self.lg.info(' [*] Verify that is the list has the config')
        httpproxy_host = [x for x in response.json() if x['host'] == body['host']]
        self.assertNotEqual(httpproxy_host, [])
        for key in body.keys():
            self.assertTrue(body[key], httpproxy_host[0][key])

    def test016_delete_httpproxyid(self):
        """ GAT-119
        **Test Scenario:**
        #. Create new httpproxy
        #. Delete httpproxy id
        #. List dhcp hosts
        #. Verify that the dhcp has been updated
        """
        self.lg.info(' [*] Create new httpproxy')
        body = {
            "host": self.random_string(),
            "destinations": ['http://192.168.2.200:500'],
            "types": ['http', 'https']
        }

        response = self.gateways_api.post_nodes_gateway_httpproxy(self.nodeid, self.gw_name, body)
        self.assertEqual(response.status_code, 201)

        self.lg.info(' [*] Delete httpproxy id')
        proxyid = body['host']
        response = self.gateways_api.delete_nodes_gateway_httpproxy(self.nodeid, self.gw_name, proxyid)
        self.assertEqual(response.status_code, 204)

        self.lg.info(' [*] List httpproxies')
        response = self.gateways_api.list_nodes_gateway_httpproxies(self.nodeid, self.gw_name)
        self.assertEqual(response.status_code, 200)

        self.lg.info(' [*] Verify that the httpproxies has been updated')
        httpproxy_host = [x for x in response.json() if x['host'] == body['host']]
        self.assertEqual(httpproxy_host, [])
