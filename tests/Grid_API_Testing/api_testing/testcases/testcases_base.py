from random import randint
import uuid
from unittest import TestCase
from api_testing.utiles.utiles import Utiles
from api_testing.grid_apis.orchestrator_client.nodes_apis import NodesAPI
from api_testing.grid_apis.orchestrator_client.containers_apis import ContainersAPI
import random, string
import requests
import time
import signal
from testconfig import config
from api_testing.grid_apis import JWT
from api_testing.testcases import NODES_INFO
from nose.tools import TimeExpired
from zeroos.orchestrator import client as apiclient

class TestcasesBase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.utiles = Utiles()
        self.nodes_api = NodesAPI()
        self.config = config['main']
        self.jwt = JWT
        self.nodes = NODES_INFO
        self.lg = self.utiles.logging
        self.session = requests.Session()
        self.zerotier_token = self.config['zerotier_token']
        self.session.headers['Authorization'] = 'Bearer {}'.format(self.zerotier_token)
        self.createdcontainer = []

    def setUp(self):
        self._testID = self._testMethodName
        self._startTime = time.time()

        def timeout_handler(signum, frame):
            raise TimeExpired('Timeout expired before end of test %s' % self._testID)

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(600)

    def randomMAC(self):
        random_mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
        mac_address = ':'.join(map(lambda x: "%02x" % x, random_mac))
        return mac_address

    def rand_str(self):
        return str(uuid.uuid4()).replace('-', '')[1:10]

    def tearDown(self):
        pass

    def get_random_node(self, except_node=None):
        response = self.nodes_api.get_nodes()
        self.assertEqual(response.status_code, 200)
        nodes_list = [x['id'] for x in response.json() if x['status']=='running']
        if nodes_list:
            if except_node is not None and except_node in nodes_list:
                nodes_list = nodes_list.remove(except_node)

        if len(nodes_list) > 0:
            node_id = nodes_list[randint(0, len(nodes_list)-1)]
            return node_id

    def random_string(self, size=10):
        return str(uuid.uuid4()).replace('-', '')[:size]

    def random_item(self, array):
        return array[randint(0, len(array)-1)]

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

    def get_random_container(self, node_id):
        container_name = self.rand_str()
        hostname = self.rand_str()
        container_body = {"name": container_name, "hostname": hostname, "flist": self.root_url,
                          "hostNetworking": False, "initProcesses": [], "filesystems": [],
                          "ports": [], "storage": "ardb://hub.gig.tech:16379"
                          }
        response = self.containers_api.get_containers(node_id)
        self.assertEqual(response.status_code, 200)
        container_list = response.json()
        counter = len(container_list)
        while (counter != 0) and (len(container_list) != 0):
            container_name = container_list[random.randint(0, len(container_list)-1)]['name']
            response = self.containers_api.get_containers_containerid(nodeid=node_id,containername=container_name)
            container=response.json()
            if container['status']=='running':
                return container_name

            else:
                counter = counter-1
        else:
            container_name = container_body["name"]
            response = self.containers_api.post_containers(nodeid=node_id, data=container_body)
            self.assertEqual(response.status_code, 201)

            if not self.wait_for_status('running', self.containers_api.get_containers_containerid,
                                                          nodeid=node_id, containername=container_name):
                return False
            else:
                self.createdcontainer.append({"node": node_id, "container": container_name})
                return container_name