import uuid, random, requests, time, signal, logging, subprocess
from unittest import TestCase
from framework.orchestrator_driver import OrchasteratorDriver
from nose.tools import TimeExpired
from testcases.core0_client import Client
from datetime import timedelta



class TestcasesBase(TestCase):
    orchasterator_driver = OrchasteratorDriver()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.utiles = Utiles()
        self.lg = self.utiles.logger()
        self.nodes_api = self.orchasterator_driver.nodes_api
        self.containers_api = self.orchasterator_driver.container_api
        self.gateways_api = self.orchasterator_driver.gateway_api
        self.bridges_api = self.orchasterator_driver.bridges_api
        self.storagepools_api = self.orchasterator_driver.storagepools_api
        self.storageclusters_api = self.orchasterator_driver.storageclusters_api
        self.vdisks_api = self.orchasterator_driver.vdisks_api
        self.vms_api = self.orchasterator_driver.vms_api
        self.backup_api = self.orchasterator_driver.backup_api
        self.graphs_api = self.orchasterator_driver.graph_apis
        self.zerotiers_api = self.orchasterator_driver.zerotiers_api
        self.zerotier_token = self.orchasterator_driver.zerotier_token
        self.vm_username = self.orchasterator_driver.vm_username
        self.vm_password = self.orchasterator_driver.vm_password
        self.nodes_info = self.orchasterator_driver.nodes_info
        self.Client = Client
        self.session = requests.Session()
        self.session.headers['Authorization'] = 'Bearer {}'.format(self.zerotier_token)

    def setUp(self):
        self._testID = self._testMethodName
        self._startTime = time.time()

        def timeout_handler(signum, frame):
            raise TimeExpired('Timeout expired before end of test %s' % self._testID)

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(540)

        self.nodeid = self.get_random_node()
        self.lg.info('Get random nodeid : %s' % str(self.nodeid))
        self.nodeipList = [x['ip'] for x in self.nodes_info if x['id'] == self.nodeid]
        self.assertNotEqual(self.nodeipList, [])
        self.nodeip = self.nodeipList[0]
        self.jwt = self.orchasterator_driver.get_jwt()
        self.core0_client = Client(self.nodeip, password=self.jwt)

    def randomMAC(self):
        random_mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff),
                      random.randint(0x00, 0xff)]
        mac_address = ':'.join(map(lambda x: "%02x" % x, random_mac))
        return mac_address

    def rand_str(self):
        return str(uuid.uuid4()).replace('-', '')[1:10]

    def tearDown(self):
        pass

    def get_random_node(self, except_node=None):
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        nodes_list = [x['id'] for x in response.json() if x['status'] == 'running']
        if nodes_list:
            if except_node is not None and except_node in nodes_list:
                nodes_list.remove(except_node)

        if len(nodes_list) > 0:
            node_id = nodes_list[random.randint(0, len(nodes_list) - 1)]
            return node_id

    def get_running_nodes(self):
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        nodes_list = [x['id'] for x in response.json() if x['status'] == 'running']
        return nodes_list

    def random_string(self, size=10):
        return str(uuid.uuid4()).replace('-', '')[:size]

    def random_item(self, array):
        return array[random.randint(0, len(array) - 1)]

    def create_zerotier_network(self, default_config=True, private=False, data={}):
        url = 'https://my.zerotier.com/api/network'

        if default_config:
            target = '10.{}.{}.0/24'.format(random.randint(1, 254), random.randint(1, 254))
            ipRangeStart = target[:-4] + '1'
            ipRangeEnd = target[:-4] + '254'
            data = {'config': {'ipAssignmentPools': [{'ipRangeEnd': ipRangeEnd,
                                                      'ipRangeStart': ipRangeStart}],
                               'private': private,
                               'routes': [{'target': target, 'via': None}],
                               'v4AssignMode': {'zt': True}}}
        response = self.session.post(url=url, json=data)
        response.raise_for_status()
        nwid = response.json()['id']
        return nwid

    def delete_zerotier_network(self, nwid):
        url = 'https://my.zerotier.com/api/network/{}'.format(nwid)
        self.session.delete(url=url)

    def wait_for_status(self, status, func, timeout=100, **kwargs):
        resource = func(**kwargs)
        if resource.status_code != 200:
            return False
        resource = resource.json()
        for _ in range(timeout):
            if resource['status'] == status:
                return True
            time.sleep(1)
            resource = func(**kwargs)
            resource = resource.json()
        return False

    def create_contaienr(self, node_id):
        name = self.random_string()
        hostname = self.random_string()
        body = {"name": name, "hostname": hostname, "flist": self.root_url,
                "hostNetworking": False, "initProcesses": [], "filesystems": [],
                "ports": [], "storage": "ardb://hub.gig.tech:16379"}

        response = self.containers_api.post_containers(nodeid=node_id, data=body)
        self.assertEqual(response.status_code, 201)
        self.createdcontainer.append({"node": node_id, "container": name})
        response = self.containers_api.get_containers_containerid(node_id, name)
        self.assertEqual(response.json()['status'], 'running')
        return name

    def get_gateway_nic(self, nics_types):
        nics = []
        for nic in nics_types:
            ip = '192.168.%i.2/24' % random.randint(1, 254)
            if nic['type'] == 'vlan':
                nic_data = {
                    "name": 'nic' + self.random_string(),
                    "type": 'vlan',
                    "id": str(random.randint(1, 4094)),
                    "config": {"cidr": ip}
                }
            elif nic['type'] == 'vxlan':
                nic_data = {
                    "name": 'nic' + self.random_string(),
                    "type": 'vxlan',
                    "id": str(random.randint(1, 100000)),
                    "config": {"cidr": ip}
                }
            elif nic['type'] == 'bridge':
                nic_data = {
                    "name": 'nic' + self.random_string(),
                    "type": 'bridge',
                    "id": nic['bridge_name'],
                    "config": {"cidr": ip}
                }
            elif nic['type'] == 'default':
                nic_data = {
                    "type": "default"
                }

            if nic['gateway']:
                nic_data['config']["gateway"] = ip[:-4] + '1'

            if nic['dhcp']:
                nic_data['dhcpserver'] = {
                    "nameservers": ['8.8.8.8'],
                    "hosts": [
                        {
                            "hostname": "hostname1",
                            "ipaddress": ip[:-4] + '10',
                            "macaddress": self.get_random_mac()
                        },
                        {
                            "hostname": "hostname2",
                            "ipaddress": ip[:-4] + '20',
                            "macaddress": self.get_random_mac()
                        }
                    ]
                }

            if nic['zerotierbridge']:
                nic_data['zerotierbridge'] = {
                    "id": nic['zerotierbridge'],
                    "token": self.zerotier_token
                }

            nics.append(nic_data)
        return nics

    def get_random_mac(self):
        random_mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff),
                      random.randint(0x00, 0xff)]
        mac_address = ':'.join(map(lambda x: "%02x" % x, random_mac))
        return mac_address

    def get_max_available_free_disks(self, nodes, disk_type=""):
        if disk_type:
            disk_types = [disk_type]
        else:
            disk_types = ['ssd', 'hdd', 'nvme']
        free_disks = []
        for nodeid in nodes:
            nodeip = [x['ip'] for x in self.nodes_info if x['id'] == nodeid][0]
            node_client = Client(ip=nodeip, password=self.jwt)
            free_disks.extend(node_client.getFreeDisks())
        return max([(sum([1 for x in free_disks if x.get('type') == y]), y) for y in disk_types])

    def get_available_free_disks(self, nodes):
        # summation of all availble disks in each type in all nodes
        disks = {"ssd": 0, "hdd": 0, "nvme": 0}

        disk_types = ['ssd', 'hdd', 'nvme']
        free_disks = []
        for nodeid in nodes:
            nodeip = [x['ip'] for x in self.nodes_info if x['id'] == nodeid][0]
            node_client = Client(ip=nodeip, password=self.jwt)
            free_disks.extend(node_client.getFreeDisks())
        for disktype in disk_types:
            disks[disktype] = sum([1 for x in free_disks if x.get('type') == disktype])
        return disks

    def get_nodes_disks(self, nodes):
        # return available disks in each node .
        # return nodes_disk dict  = {"nodeid":{"ssd": 0, "hdd": 0, "nvme": 0}}

        nodes_disk = {}
        for nodeid in nodes:
            disks = {"ssd": 0, "hdd": 0, "nvme": 0}
            nodeip = [x['ip'] for x in self.nodes_info if x['id'] == nodeid][0]
            node_client = Client(ip=nodeip, password=self.jwt)
            node_disks = node_client.getFreeDisks()
            for disk in list(disks.keys()):
                for x in node_disks:
                    if x.get('type') == disk:
                        disks[disk]+=1
            nodes_disk[nodeid] = disks
        return nodes_disk

    def get_nodes_disks_sum(self, nodes):
        # retrun summation of each disk type, and list of nodes which contain this type.

        nodes_disks_info = {"ssd": {'sum': 0,
                                    'nodes': []},
                            "hdd": {'sum': 0,
                                    'nodes': []},
                            "nvme": {'sum': 0,
                                     'nodes': []}
                            }

        nodes_disks = self.get_nodes_disks(nodes)
        for node_id in nodes_disks:
            for key in nodes_disks_info:
                if nodes_disks[node_id][key] != 0:
                    nodes_disks_info[key]['sum'] += nodes_disks[node_id][key]
                    nodes_disks_info[key]['nodes'].append(node_id)
        return nodes_disks_info

    def block_cluster_creation(self, nodes):
        # return block custer data, available servers , disktype,nodes.
        block_cluster = {"servers": 0, "type": "", "nodes": []}

        nodes_disks_info = self.get_nodes_disks_sum(nodes)
        nodes_disks = self.get_nodes_disks(nodes)
        disks = {"ssd": nodes_disks_info["ssd"]["sum"],
                 "hdd": nodes_disks_info["hdd"]["sum"],
                 "nvme": nodes_disks_info["nvme"]["sum"]
                }
        tmp = dict(disks)
        for disk_type in disks:
            maxdisk = max(tmp, key=tmp.get)
            nodes = nodes_disks_info[maxdisk]["nodes"]
            if not nodes:
                continue
            while (tmp[maxdisk] % len(nodes)):
                tmp[maxdisk] -=1
            servers_per_node = int(tmp[maxdisk]/len(nodes))
            for nodeid in nodes:
                if (nodes_disks[nodeid][maxdisk] < servers_per_node):
                    break
            else:
                block_cluster = {"servers": tmp[maxdisk], "type": maxdisk,
                                 "nodes": nodes_disks_info[maxdisk]["nodes"]}
                return block_cluster
        else:
            maxdisk = max(disks, key=disks.get)
            block_cluster = {"servers": len(nodes_disks_info[maxdisk]["nodes"]), "type": maxdisk,
                             "nodes": nodes_disks_info[maxdisk]["nodes"]}
            return block_cluster

    def get_clusters_data(self, nodes):
        ### this method return dict with object cluster and block cluster data and servers
        clusters_data = {"blockcluster": {"servers": 0, "nodes": [], "type": ""},
                         "objectcluster": {"nodes": [], "drivetype": "", "metadatatype": ""}
                         }

        disk_types = ["ssd", "hdd", "nvme"]
        blockcluster = self.block_cluster_creation(nodes)
        max_disktype = blockcluster["type"]
        disk_types.remove(max_disktype)
        object_max_type = {"nodes": [], "drivetype": max_disktype, "metadatatype": max_disktype}
        object_type1 = {"nodes": [], "drivetype": disk_types[0], "metadatatype": disk_types[0]}
        object_type2 = {"nodes": [], "drivetype": disk_types[1], "metadatatype": disk_types[1]}
        object_edintecal_types = {"nodes": [], "drivetype": disk_types[1], "metadatatype": disk_types[0]}
        node_disks = self.get_nodes_disks(nodes)

        # *for_packet_machines* #
        free_disks = sum([node_disks[nodeid][disk_types[0]] + node_disks[nodeid][disk_types[1]] for nodeid in nodes])
        if not free_disks and blockcluster["servers"]:
            tmp = blockcluster["servers"]
            tmp = tmp - 2*len(blockcluster["nodes"])
            if not tmp%len(blockcluster["nodes"]) and tmp > 0:
                blockcluster["servers"]=tmp
                object_max_type["nodes"] = blockcluster["nodes"]
                clusters_data["blockcluster"] = blockcluster
                clusters_data["objectcluster"] = object_max_type
                return clusters_data
        #############################

        for nodeid in nodes:
            free_disks = node_disks[nodeid][disk_types[0]] + node_disks[nodeid][disk_types[1]]
            if free_disks < 2:
                remain_max_servers = node_disks[nodeid][max_disktype]-(blockcluster["servers"]/len(blockcluster["nodes"]))
                if remain_max_servers >=2:
                    object_max_type["nodes"].append(nodeid)
            else:
                if node_disks[nodeid][disk_types[0]] >= 2:
                    object_type1["nodes"].append(nodeid)

                elif node_disks[nodeid][disk_types[1]] >=2:
                    object_type2["nodes"].append(nodeid)

                elif (node_disks[nodeid][disk_types[1]]==1) and (node_disks[nodeid][disk_types[0]]==1):
                    object_edintecal_types["nodes"].append(nodeid)
        options = [object_max_type, object_type1, object_type2, object_edintecal_types]
        nodes_number, objectcluster = max([(len(y["nodes"]), y) for y in options],key=lambda x:x[0])

        clusters_data["blockcluster"] = blockcluster
        clusters_data["objectcluster"] = objectcluster
        return clusters_data

    def get_available_cluster_type(self, clusters, clustertype):
        for cluster in clusters:
            response = self.storageclusters_api.get_storageclusters_label(cluster)
            self.assertEqual(response.status_code,
                             200)
            if response.json()["clusterType"] == clustertype:
                return response.json()["label"]
        return ""

    def create_object_cluster(self, objectcluster_data):
        nodes = objectcluster_data["nodes"]
        servers = len(nodes)
        driveType = objectcluster_data["drivetype"]
        metaDriveType = objectcluster_data["metadatatype"]
        parityshards = random.randint(1,len(nodes)-1)
        datashards = len(nodes) - parityshards
        serversPerMetaDrive = 1
        response, cluster = self.storageclusters_api.post_object_cluster(nodes=nodes,
                                                                         driveType=driveType,
                                                                         metaDriveType=metaDriveType,
                                                                         servers=servers,
                                                                         dataShards=datashards,
                                                                         parityShards=parityshards,
                                                                         serversPerMetaDrive =serversPerMetaDrive
                                                                         )
        return response, cluster


    def enable_ssh_access(self, vnc_ip, username=None, password=None, zerotier_nwid=None):

        username = username or self.vm_username
        password = password or self.vm_password

        """
            Add ssh key to a vm with active vnc protocol.
        """
        vnc = 'vncdotool -s %s' % vnc_ip
        commands = [
            '%s' % username,
            '%s' % password,
            'sudo su',
            '%s' % password,
            'sed -i "s/PasswordAuthentication no/PasswordAuthentication yes/g" /etc/ssh/sshd',
            'service sshd restart'
        ]

        if zerotier_nwid:
            zerotier_commands = [
                'curl -s https',
                '//install.zerotier.com -o zr.sh',
                'bash zr.sh',
                'zerotier-cli join %s' % zerotier_nwid
            ]
            commands.extend(zerotier_commands)

        for cmd in commands:
            if "sed" in cmd:
                self.utiles.execute_shell_commands(cmd="%s type %s" % (vnc, repr(cmd)))
                self.utiles.execute_shell_commands(cmd="%s key shift-_ type config key enter" % vnc)
                time.sleep(1)
            elif 'https' in cmd:
                self.utiles.execute_shell_commands(cmd="%s type %s" % (vnc, repr(cmd)))
                self.utiles.execute_shell_commands(cmd="%s key shift-:" % vnc)
            else:
                self.utiles.execute_shell_commands(cmd="%s type %s key enter" % (vnc, repr(cmd)))
                time.sleep(1)

    def get_vm_default_ipaddress(self, vmname):
        cmd = "virsh dumpxml {} | grep 'mac address' | cut -d '=' -f2 | cut -d '/' -f1".format(vmname)
        vm_mac_addr = self.core0_client.client.bash(cmd).get().stdout.strip()

        cmd = "arp | grep {} | cut -d '(' -f2 | cut -d ')' -f1".format(vm_mac_addr)
        for i in range(20):
            vm_ip_addr = self.core0_client.client.bash(cmd).get().stdout.strip()
            if vm_ip_addr:
                break
            else:
                time.sleep(5)

        return vm_ip_addr


    def execute_command_inside_vm(self, client, vmip,  cmd, username=None, password=None):
        username = username or self.vm_username
        password = password or self.vm_password

        cmd = 'sshpass -p "{password}" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 {username}@{vmip} "{cmd}"'.format(
            vmip=vmip,
            username=username,
            password=password,
            cmd=cmd
        )

        response = client.bash(cmd).get()
        return response

class Utiles:

    def logger(self):
        logger = logging.getLogger('0-Orchestrator')
        if not logger.handlers:
            fileHandler = logging.FileHandler('test_suite.log', mode='w')
            formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)

        return logger


    def execute_shell_commands(self, cmd):
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = process.communicate()
        return out.decode('utf-8'), error.decode('utf-8')
