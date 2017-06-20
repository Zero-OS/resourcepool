import time
from termcolor import colored
from install_testing_nodes.src.Basic import Basic


class RequestEnvAPI(Basic):
    def __init__(self):
        super(RequestEnvAPI, self).__init__()
        self.get_client()
        self.cloudspace = {}
        self.virtualmachine = {}
        self.ubunutu_16_image_id = self.get_ubuntu_16_image_id()

    def create_account(self):
        if not self.values['account']:
            self.logging.info(' [*] Create new account .... ')
            print(colored(' [*] Create new account .... ', 'white'))
            self.account = self.random_string()
            api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/account/create'
            client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                             'Accept': 'application/json'}
            client_data = {'name': self.account,
                           'username': self.values['username'],
                           'maxMemoryCapacity': -1,
                           'maxVDiskCapacity': -1,
                           'maxCPUCapacity': -1,
                           '&maxNASCapacity': - 1,
                           'maxArchiveCapacity': -1,
                           'maxNetworkOptTransfer': - 1,
                           'maxNetworkPeerTransfer': - 1,
                           'maxNumPublicIP': - 1,
                           'location': self.values['location']}
            client_response = self.client._session.post(url=api, headers=client_header, data=client_data)

            if client_response.status_code == 200:
                self.account_id = client_response.text
                self.values['account'] = self.account
                self.logging.info(' [+] DONE : Create %s : %s account\n' % (self.account, self.account_id))
                print(colored(' [+] DONE : Create %s : %s account\n' % (self.account, self.account_id), 'green'))
            else:
                self.logging.error(colored(
                    ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content)),
                    'red')
                print(colored(
                    ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content)),
                    'red')
                client_response.raise_for_status()
        else:
            self.account = self.values['account']
            self.get_account_ID(self.account)
            self.logging.info(' [*] Use %s account' % self.values['account'])
            print(colored(' [*] Use %s account' % self.values['account'], 'green'))

    def get_account_ID(self, account):
        self.logging.info(' [*] Get %s account ID .... ' % account)
        print(colored(' [*] Get %s account ID .... ' % account, 'white'))

        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/accounts/list'
        client_response = self.client._session.post(url=api, headers=self.client_header)

        if client_response.status_code == 200:
            for element in client_response.json():
                if account == element['name']:
                    self.account_id = element['id']
                    self.logging.info(' [+] DONE : Account ID : % d\n' % self.account_id)
                    print(colored(' [+] DONE : Account ID : % d\n' % self.account_id))
                    break
            else:
                self.logging.error(
                    " [-] ERROR : Can't get %s account ID. Please, Make sure that %s username can get this account ID" % (
                        account, self.values['username']))
                print(colored(
                    " [-] ERROR : Can't get %s account ID. Please, Make sure that %s username can get this account ID" % (
                        account, self.values['username']), 'red'))
                raise NameError(
                    " [*] ERROR : Can't get '%s' account ID. Please, Make sure that '%s' username can get this account ID" % (
                        account, self.values['username']))
        else:
            self.logging.error(' [*] ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' [*] ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def create_cloudspace(self):
        self.logging.info(' [*] Create new cloudspace .... ')
        print(colored(' [*] Create new cloudspace .... ', 'white'))
        self.cloudspace['name'] = self.random_string()
        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/cloudspace/create'
        client_data = {
            'accountId': self.account_id,
            'name': self.cloudspace['name'],
            'access': self.values['username'],
            'username': self.values['username'],
            'maxMemoryCapacity': -1,
            'maxVDiskCapacity': -1,
            'maxCPUCapacity': -1,
            '&maxNASCapacity': - 1,
            'maxArchiveCapacity': -1,
            'maxNetworkOptTransfer': - 1,
            'maxNetworkPeerTransfer': - 1,
            'maxNumPublicIP': - 1,
            'location': self.values['location']}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.cloudspace['id'] = client_response.text
            self.logging.info(' [+] DONE : Create %s cloudspace\n' % self.cloudspace['name'])
            print(colored(' [+] DONE : Create %s cloudspace\n' % self.cloudspace['name'], 'green'))
        else:
            self.logging.error(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
            print(colored(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content)))
            client_response.raise_for_status()

    def create_virtualmachine(self):
        self.logging.info(' [*] Create new virtual mahcine .... ')
        print(colored(' [*] Create new virtual mahcine .... ', 'white'))
        self.virtualmachine['name'] = self.random_string()

        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/machine/create'

        client_data = {
            'cloudspaceId': self.cloudspace['id'],
            'name': self.virtualmachine['name'],
            'sizeId': 3,
            'imageId': self.ubunutu_16_image_id,
            'disksize': 20}

        for _ in range(5):
            client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)
            if client_response.status_code == 200:
                self.virtualmachine['id'] = client_response.text
                self.logging.info(
                    ' [+] DONE : Create %s : %s virtual machine\n' % (self.virtualmachine['name'], self.virtualmachine['id']))
                print(colored(' [+] DONE : Create %s : %s virtual machine\n' % (self.virtualmachine['name'], self.virtualmachine['id']), 'green'))
                self.get_virtualmachine_password()
                break
            else:
                self.logging.error(
                    ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
                print(colored(
                    ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content),
                    'red'))
                time.sleep(1)
                continue
        else:
            client_response.raise_for_status()

    def get_ubuntu_16_image_id(self):
        self.logging.info(' [*] Get the Ubunut 16.04 id')
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/images/list'
        client_response = self.client._session.post(url=api, headers=self.client_header)
        if client_response.status_code == 200:

            for temp in list(client_response.json()):
                if 'Ubuntu 16.04' in temp['name']:
                    self.image_id = temp['id']
                    self.logging.info(' [+] The Ubunut 16.04 id is %s' % self.image_id)
                    return self.image_id
        else:
            self.logging.error(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
            client_response.raise_for_status()

    def create_port_forward(self, publicPorts):
        if 'ip' not in self.cloudspace.keys():
            self.get_cloudspace_ip()

        for key in publicPorts:
            self.logging.info(' [*] START : port forward creation ...')
            print(colored(' [*] START : port forward creation ...'))
            api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/portforwarding/create'
            client_data = {'cloudspaceId': self.cloudspace['id'],
                           'publicIp': self.cloudspace['ip'],
                           'publicPort': publicPorts[key],
                           'machineId': self.virtualmachine['id'],
                           'localPort': key,
                           'protocol': 'tcp'}
            for _ in range(100):
                try:
                    client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)
                    if client_response.status_code == 200:
                        self.logging.info(' [+] DONE : forward local %i to %i' % (key, publicPorts[key]))
                        print(colored(' [+] DONE : forward local %i to %i' % (key, publicPorts[key]), 'green'))
                        break
                    else:
                        client_response.raise_for_status()
                except:
                    time.sleep(2)
            else:
                self.logging.error(
                    ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
                print(colored(
                    ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content),
                    'red'))
                client_response.raise_for_status()

    def get_cloudspace_ip(self):
        self.logging.info(' [*] START : get cloudspace IP ...')
        print(colored(' [*] START : get cloudspace IP ...', 'white'))
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/cloudspaces/get'
        client_data = {'cloudspaceId': self.cloudspace['id']}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.cloudspace['ip'] = client_response.json()['publicipaddress']
            self.logging.info(' [+] cloudpsace public IP : %s \n' % self.cloudspace['ip'])
            print(colored(' [+] cloudpsace public IP : %s \n' % self.cloudspace['ip'], 'green'))
        else:
            self.logging.error(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
            print(colored(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content),
                'red'))
            client_response.raise_for_status()

    def get_virtualmachine_password(self):
        self.logging.info(' [*] START : get virtual machine password ...')
        print(colored(' [*] START : get virtual machine password ...', 'white'))
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/machines/get'
        client_data = {'machineId': self.virtualmachine['id']}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.virtualmachine['password'] = client_response.json()['accounts'][0]['password']
            self.logging.info(' [+] Virtual machine password : %s\n' % self.virtualmachine['password'])
            print(colored(' [+] Virtual machine password : %s\n' % self.virtualmachine['password'], 'green'))
        else:
            self.logging.error(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
            print(colored(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content),
                'red'))
            client_response.raise_for_status()

    def delete_cloudspace(self):
        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/cloudspace/destroy'
        client_data = {'accountId': self.account_id,
                       'cloudspaceId': self.cloudspace['id'],
                       'reason': 'Test'}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.logging.info(' [*] Delete %s cloudspace' % self.cloudspace['name'])
        else:
            self.logging.error(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
            print(colored(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content),
                'red'))
            client_response.raise_for_status()

    def get_virtualmachine_ip(self):
        self.logging.info(' [*] START : get virtual machine IP ...')
        print(colored(' [*] START : get virtual machine IP ...', 'white'))
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/machines/get'
        client_data = {'machineId': self.virtualmachine['id']}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.virtualmachine['ip'] = client_response.json()['interfaces'][0]['ipAddress']
            self.logging.info(' [+] Virtual machine ip : %s\n' % self.virtualmachine['ip'])
            print(colored(' [+] Virtual machine ip : %s\n' % self.virtualmachine['ip'], 'green'))
        else:
            self.logging.error(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content))
            print(colored(
                ' [-] ERROR : response status code %i %s' % (client_response.status_code, client_response.content),
                'red'))
            client_response.raise_for_status()
