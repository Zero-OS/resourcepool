from zeroos.core0.client import Client as core0_client
import time


class Client:
    def __init__(self, ip):
        self.client = core0_client(ip)

    def stdout(self, resource):
        return resource.get().stdout.replace('\n', '').lower()

    def get_nodes_cpus(self):
        info = self.client.info.cpu()
        cpuInfo = []
        for processor in info:
            cpuInfo.append(processor)
        return cpuInfo

    def get_nodes_nics(self):
        r = self.client.bash('ip -br a').get().stdout
        nics = [x.split()[0] for x in r.splitlines()]
        nicInfo = []
        for nic in nics:
            if '@' in nic:
                nic = nic[:nic.index('@')]
            addrs = self.client.bash('ip -br a show "{}"'.format(nic)).get()
            addrs = addrs.stdout.splitlines()[0].split()[2:]
            mtu = int(self.stdout(self.client.bash('cat /sys/class/net/{}/mtu'.format(nic))))
            hardwareaddr = self.stdout(self.client.bash('cat /sys/class/net/{}/address'.format(nic)))
            if hardwareaddr == '00:00:00:00:00:00':
                    hardwareaddr = ''
            addrs = [ x for x in addrs]
            if addrs == [] :
                addrs= None
            tmp = {"name": nic, "hardwareaddr": hardwareaddr, "mtu": mtu, "addrs": addrs}
            nicInfo.append(tmp)

        return nicInfo

    def get_node_bridges(self):
        bridgesInfo = []
        nics = self.client.bash('ls /sys/class/net').get().stdout.splitlines()
        for nic in nics:
            status = self.client.bash('cat /sys/class/net/{}/operstate'.format(nic)).get().stdout.strip()
            bridge = {"name":nic, "status":status}
            bridgesInfo.append(bridge)

        return bridgesInfo

    def get_nodes_mem(self):
        lines = self.client.bash('cat /proc/meminfo').get().stdout.splitlines()
        memInfo = {'available': 0, 'buffers': 0, 'cached': 0,
                    'inactive': 0, 'total': 0}
        for line in lines:
            line = line.replace('\t', '').strip()
            key = line[:line.find(':')].lower()
            value = line[line.find(':')+2:line.find('kB')].strip()
            if 'mem' == key[:3]:
                key = key[3:]
            if key in memInfo.keys():

                memInfo[key] = int(value)*1024
        return memInfo

    def get_nodes_info(self):
        hostname = self.client.system('uname -n').get().stdout.strip()
        krn_name = self.client.system('uname -s').get().stdout.strip().lower()
        return {"hostname":hostname, "os":krn_name}

    def get_nodes_disks(self):
        disks_info = []
        disks = self.client.disk.list()['blockdevices']
        for disk in disks:
            disk_type = None
            disk_parts = []
            if 'children' in disk.keys():
                for part in disk['children']:
                    disk_parts.append({
                        "name": '/dev/{}'.format(part['name']),
                        "size": int(int(part['size'])/1073741824),
                        "partuuid": part['partuuid'],
                        "label": part['label'],
                        "fstype": part['fstype']
                    })

            if int(disk['rota']):
                if int(disk['size']) > (1073741824**1024*7):
                    disk_type = 'archive'
                else:
                    disk_type = 'hdd'
            else:
                if 'nvme' in disk['name']:
                    disk_type = 'nvme'
                else:
                    disk_type = 'ssd'
            
            disks_info.append({
                "device": '/dev/{}'.format(disk['name']),
                "size": int(int(disk['size'])/1073741824),
                "type": disk_type,
                "partitions": disk_parts
            })

        return disks_info


    def get_jobs_list(self):
        jobs = self.client.job.list()
        gridjobs = []
        temp = {}
        for job in jobs:
            temp['id'] = job['cmd']['id']
            if job['cmd']['arguments']:
                if ('name' in job['cmd']['arguments'].keys()):
                    temp['name'] = job['cmd']['arguments']['name']
            temp['starttime'] = job['starttime']
            gridjobs.append(temp)
        return gridjobs

    def get_node_state(self):
        state = self.client.json('core.state', {})
        del state['cpu']
        return state

    def start_job(self):
        job_id = self.client.system("tailf /etc/nsswitch.conf").id
        jobs = self.client.job.list()
        for job in jobs:
            if job['cmd']['id'] == job_id:
                return job_id
        return False

    def start_process(self):
        self.client.system("tailf /etc/nsswitch.conf")
        processes = self.get_processes_list()
        for process in processes:
            if process['cmdline'] == "tailf /etc/nsswitch.conf":
                return process['pid']
        return False

    def getFreeDisks(self):
        freeDisks = []
        disks = self.client.disk.list()['blockdevices']
        for disk in disks:
            if not disk['mountpoint'] and disk['kname'] != 'sda':
                if 'children' not in disk.keys():
                    freeDisks.append('/dev/{}'.format(disk['kname']))
                else:
                    for children in disk['children']:
                        if children['mountpoint']:
                            break
                    else:
                        freeDisks.append('/dev/{}'.format(disk['kname']))

        return freeDisks

    def get_processes_list(self):
        processes = self.client.process.list()
        return processes

    def get_container_client(self,container_name):
        container = self.client.container.find(container_name)
        if not container:
            return False
        container_id = list(container.keys())[0]
        container_client = self.client.container.client(int(container_id))
        return container_client

    def get_container_info(self, container_id):
        container = (self.client.container.find(container_id))
        if not container:
            return False
        container_id=list(container.keys())[0]
        container_info = {}
        golden_data = self.client.container.list().get(str(container_id), None)
        if not golden_data:
            return False
        golden_value = golden_data['container']
        container_info['nics'] = ([{i: nic[i] for i in nic if i != 'hwaddr'} for nic in golden_value['arguments']['nics']])
        container_info['ports'] = (['%s:%s' % (key, value) for key, value in golden_value['arguments']['port'].items()])
        container_info['hostNetworking'] = golden_value['arguments']['host_network']
        container_info['hostname'] = golden_value['arguments']['hostname']
        container_info['flist'] = golden_value['arguments']['root']
        container_info['storage'] = golden_value['arguments']['storage']
        return container_info

    def get_container_job_list(self, container_name):
        container_id = list(self.client.container.find(container_name).keys())[0]
        golden_values = []
        container = self.client.container.client(int(container_id))
        container_data = container.job.list()
        # cannot compare directly as the job.list is considered a job and has a different id everytime is is called
        for i, golden_value in enumerate(container_data[:]):
            if golden_value.get('command', "") == 'job.list':
                container_data.pop(i)
                continue
            golden_values.append((golden_value['cmd']['id'], golden_value['starttime']))
        return set(golden_values)

    def wait_on_container_update(self, container_name, timeout, removed):
        for _ in range(timeout):
            if removed:
                if not self.client.container.find(container_name):
                    return True
            else:
                if self.client.container.find(container_name):
                    return True
            time.sleep(1)
        return False

    def wait_on_container_job_update(self, container_name, job_id, timeout, removed):
        container_id = int(list(self.client.container.find(container_name).keys())[0])
        container = self.client.container.client(container_id)
        for _ in range(timeout):
            if removed:
                if job_id not in [item['cmd']['id']for item in container.job.list()]:
                    return True
            else:
                if job_id in [item['cmd']['id']for item in container.job.list()]:
                    return True
            time.sleep(1)
        return False

    def get_client_zt_ip(self, client):
        nics = client.info.nic()
        nic = [nic for nic in nics if 'zt' in nic['name']]
        if not nic :
            return False
        address = nic[0]['addrs'][0]['addr']
        if not address:
            self.lg('can\'t find zerotier netowrk interface')
            return False
        return address[:address.find('/')]

    def get_container_bridge_ip(self, client,ip_range):
        nics = client.info.nic()

        nic = [nic for nic in nics if nic['name'] == 'eth0']
        if not nic :
            return False
        addresses = [x['addr'] for x in nic[0]['addrs'] if x['addr'][:x['addr'].find('/')] in ip_range]
        if not addresses:
            return False
        address = addresses[0]

        if not address:
            self.lg('can\'t find bridge netowrk interface')
            return False
        return address[:address.find('/')]

    def check_container_vlan_vxlan_ip(self, client, cidr_ip):
        nics = client.info.nic()

        nic = [nic for nic in nics if nic['name'] == 'eth1']
        if not nic :
            return False
        address = [x['addr'] for x in nic[0]['addrs'] if x['addr'][:x['addr'].find('/')] == cidr_ip][0]
        if not address:
            self.lg('can\'t find netowrk interface')
            return False
        return True

    def create_ovs_container(self):
        containers = self.client.container.find('ovs')
        ovs_exist = [key for key, value in containers.items()]
        if not ovs_exist:
            ovs_flist = "https://hub.gig.tech/gig-official-apps/ovs.flist"
            ovs = int(self.client.container.create(ovs_flist, host_network=True , tags=['ovs']).get().data)
            ovs_client = self.client.container.client(ovs)
            time.sleep(2)
            ovs_client.json('ovs.bridge-add', {"bridge": "backplane"})
            ovs_client.json('ovs.vlan-ensure', {'master': 'backplane', 'vlan': 2000, 'name': 'vxbackend'})
