import time, requests, os, uuid, logging, configparser
from subprocess import Popen, PIPE
from install_testing_nodes.src.client import Client
from random import randint
from termcolor import colored


class Basic(object):
    ZEROTIER_NW_ID = None

    def __init__(self):
        self.clone = False
        self.account = ''
        self.account_id = ''
        self.logging = logging
        self.log('install_testing_nodes/install_testing_nodes.log')
        self.values = {'environment': '',
                       'username': '',
                       'password': '',
                       'location': '',
                       'packet_username': '',
                       'packer_password': ''
                       }
        self.g8os_ip_list = []
        self.client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                              'Accept': 'application/json'}
        self.requests = requests
        self.setup()

    def setup(self):
        self.get_config_values()
        if not self.values['password']:
            self.values['password'] = str(input("Please, Enter %s's password : " % self.values['username']))
        self.get_g8os_ips()

    def get_config_values(self):
        script_dir = os.path.dirname(__file__)
        config_file = "../config.ini"
        config_path = os.path.join(script_dir, config_file)
        config = configparser.ConfigParser()
        config.read(config_path)
        section = config.sections()[0]
        options = config.options(section)
        for option in options:
            value = config.get(section, option)
            self.values[option] = value

    def run_cmd_via_subprocess(self, cmd):
        sub = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
        out, err = sub.communicate()
        if sub.returncode == 0:
            return out.decode('utf-8')
        else:
            error_output = err.decode('utf-8')
            raise RuntimeError("Failed to execute command.\n\ncommand:\n{}\n\n".format(cmd, error_output))

    def log(self, log_file_name='log.log'):
        self.logging.basicConfig(filename=log_file_name, filemode='w', level=logging.INFO,
                                 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        '''
        How to use:
            self.logging.debug("This is a debug message")
            self.logging.info("Informational message")
            self.logging.error("An error has happened!")
        '''

    def get_client(self):
        for _ in range(30):
            try:
                self.client = Client('https://' + self.values['environment'], self.values['username'],
                                     self.values['password'])
                break
            except:
                time.sleep(1)
        else:
            self.client = Client('https://' + self.values['environment'], self.values['username'],
                                 self.values['password'])

    @staticmethod
    def random_string():
        return str(uuid.uuid4()).replace("-", "")[:10]

    @staticmethod
    def random_integer(min_val, max_val):
        return randint(int(min_val), int(max_val))

    def get_g8os_ips(self):
        for i in range(10):
            check = 'g8os_ip_%i' % i
            if check in self.values.keys():
                self.g8os_ip_list.append([self.values[check], self.values['g8os_mac_%i' % i]])

    def get_discovering_blueprint(self, auto_discovering=False):
        blueprint = ''

        if auto_discovering:
            blueprint = """bootstrap.g8os__grid1:\\n  zerotierNetID: %s\\n  zerotierToken: '"%s"' \\n\\nactions:\\n  - action: install\\n \\n """ % (
                self.ZEROTIER_NW_ID, self.values['zerotier_token'])
        else:
            for g8os in self.g8os_ip_list:
                if ':' in g8os[1]:
                    g8os[1] = g8os[1].replace(':', '')
                tmp = "node.g8os__%s:\\n  redisAddr: %s\\n \\n" % (g8os[1], g8os[0])
                blueprint += tmp
        return blueprint

    def build_discovering_blueprint(self):
        pass

    def authorize_zerotire_member(self, member):
        self.logging.info(' [*] Authorized zerotire %s member ... ' % member)
        print(colored(' [*] Authorized zerotire %s member ... ' % member))
        session = requests.Session()
        session.headers['Authorization'] = 'Bearer %s' % self.values['zerotier_token']
        url = 'https://my.zerotier.com/api/network/%s/member/%s' % (self.ZEROTIER_NW_ID, member)
        data = {'config': {'authorized': True}}
        response = session.post(url=url, json=data)
        response.raise_for_status()

    def create_zerotire_nw(self, use_this_nw):
        if use_this_nw:
            Basic.ZEROTIER_NW_ID = use_this_nw
        else:
            self.logging.info(' [*] Create new zerotier network ... ')
            session = requests.Session()
            session.headers['Authorization'] = 'Bearer %s' % self.values['zerotier_token']
            url = 'https://my.zerotier.com/api/network'
            data = {'config': {'ipAssignmentPools': [{'ipRangeEnd': '10.147.17.254',
                                                      'ipRangeStart': '10.147.17.1'}],
                               'private': 'true',
                               'routes': [{'target': '10.147.17.0/24', 'via': None}],
                               'v4AssignMode': {'zt': 'true'}}}

            response = session.post(url=url, json=data)
            response.raise_for_status()
            Basic.ZEROTIER_NW_ID = response.json()['id']
            self.logging.info(' [*] %s zerotier nw has been created... ' % self.ZEROTIER_NW_ID)
            print(colored(' [*] %s zerotier nw has been created... \n' % self.ZEROTIER_NW_ID, 'green'))
