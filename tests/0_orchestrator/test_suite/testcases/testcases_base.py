import uuid, random, requests, time, signal, logging
from unittest import TestCase
from framework.orchestrator_driver import OrchasteratorDriver
from nose.tools import TimeExpired
from testcases.core0_client import Client


class TestcasesBase(TestCase):
    orchasterator_driver = OrchasteratorDriver()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.utiles = Utiles()
        self.lg = self.utiles.logging

        self.nodes_api = self.orchasterator_driver.nodes_api
        self.containers_api = self.orchasterator_driver.container_api
        self.gateways_api = self.orchasterator_driver.gateway_api
        self.bridges_api = self.orchasterator_driver.bridges_api
        self.storagepools_api = self.orchasterator_driver.storagepools_api
        self.storageclusters_api = self.orchasterator_driver.storageclusters_api
        self.vdisks_api = self.orchasterator_driver.vdisks_api
        self.vms_api = self.orchasterator_driver.vms_api
        self.zerotiers_api = self.orchasterator_driver.zerotiers_api

        self.zerotier_token = self.orchasterator_driver.zerotier_token
        self.jwt = self.orchasterator_driver.JWT
        self.nodes_info = self.orchasterator_driver.nodes_info

        self.session = requests.Session()
        self.session.headers['Authorization'] = 'Bearer {}'.format(self.zerotier_token)

    def setUp(self):
        self._testID = self._testMethodName
        self._startTime = time.time()

        def timeout_handler(signum, frame):
            raise TimeExpired('Timeout expired before end of test %s' % self._testID)

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(600)

        self.nodeid = self.get_random_node()
        self.lg.info('Get random nodeid : %s' % str(self.nodeid))
        core0_ip = [x['ip'] for x in self.nodes_info if x['id'] == self.nodeid]
        self.assertNotEqual(core0_ip, [])
        self.core0_client = Client(core0_ip[0], password=self.jwt)

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
                nodes_list = nodes_list.remove(except_node)

        if len(nodes_list) > 0:
            node_id = nodes_list[random.randint(0, len(nodes_list) - 1)]
            return node_id

    def random_string(self, size=10):
        return str(uuid.uuid4()).replace('-', '')[:size]

    def random_item(self, array):
        return array[random.randint(0, len(array) - 1)]

    def create_zerotier_network(self, private=False):
        url = 'https://my.zerotier.com/api/network'
        data = {'config': {'ipAssignmentPools': [{'ipRangeEnd': '10.147.17.254',
                                                  'ipRangeStart': '10.147.17.1'}],
                           'private': private,
                           'routes': [{'target': '10.147.17.0/24', 'via': None}],
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
                    "name": self.random_string(),
                    "type": 'vlan',
                    "id": str(random.randint(1, 4094)),
                    "config": {"cidr": ip}
                }
            elif nic['type'] == 'vxlan':
                nic_data = {
                    "name": self.random_string(),
                    "type": 'vxlan',
                    "id": str(random.randint(1, 100000)),
                    "config": {"cidr": ip}
                }
            elif nic['type'] == 'bridge':
                nic_data = {
                    "name": self.random_string(),
                    "type": 'bridge',
                    "id": nic['bridge_name'],
                    "config": {"cidr": ip}
                }

            if nic['gateway']:
                nic_data['config']["gateway"] = ip[:-4] + '1'

            if nic['dhcp']:
                nic_data['dhcpserver'] = {
                    "nameservers": ['8.8.8.8'],
                    "hosts": [
                        {
                            "hostname": "hostname1",
                            "ipaddress": ip[:-4]+'10',
                            "macaddress": self.get_random_mac()
                        },
                        {
                            "hostname": "hostname2",
                            "ipaddress": ip[:-4]+'20',
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

class Utiles:
    def __init__(self):
        self.config = {}
        self.logging = logging
        self.log('test_suite.log')

    def log(self, log_file_name='log.log'):
        log = self.logging.getLogger()
        fileHandler = self.logging.FileHandler(log_file_name)
        log.addHandler(fileHandler)
        self.logging.basicConfig(filename=log_file_name, filemode='rw', level=logging.INFO,
                                 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
