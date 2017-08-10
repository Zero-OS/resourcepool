#!/usr/bin/python3
from random import randint
import packet
import time
import sys
import subprocess
import requests


def create_new_device(manager, hostname, zt_net_id, itsyouonline_org, branch='master'):
    project = manager.list_projects()[0]
    ipxe_script_url = 'https://bootstrap.gig.tech/ipxe/{}/{}/organization={}'.format(branch, zt_net_id,
                                                                                     itsyouonline_org)
    print(' [*] creating new machine: {}  .. '.format(hostname))
    device = manager.create_device(project_id=project.id,
                                   hostname=hostname,
                                   plan='baremetal_2',
                                   operating_system='custom_ipxe',
                                   ipxe_script_url=ipxe_script_url,
                                   facility='ams1')
    return device


def delete_devices(manager, hostname):
    project = manager.list_projects()[0]
    devices = manager.list_devices(project.id)
    for dev in devices:
        if dev.hostname == hostname:
            device_id = dev.id
            params = {
                "hostname": dev.hostname,
                "description": "string",
                "billing_cycle": "hourly",
                "userdata": "",
                "locked": False,
                "tags": []
            }
            manager.call_api('devices/%s' % device_id, type='DELETE', params=params)


def create_pkt_machine(manager, zt_net_id, itsyouonline_org, branch='master'):
    hostname = 'orch{}-travis'.format(randint(100, 300))
    try:
        device = create_new_device(manager, hostname, zt_net_id, itsyouonline_org, branch=branch)
    except:
        print(' [*] device hasn\'t been created')
        raise

    print(' [*] provisioning the new machine ..')
    while True:
        dev = manager.get_device(device.id)
        if dev.state == 'active':
            print(' [*] The new machine is active now.')
            break
    time.sleep(5)
    return hostname

def create_zerotire_nw(zt_token):
    print(' [*] Create new zerotier network ... ')
    session = requests.Session()
    session.headers['Authorization'] = 'Bearer %s' % zt_token
    url = 'https://my.zerotier.com/api/network'
    data = {'config': {'ipAssignmentPools': [{'ipRangeEnd': '10.147.17.254',
                                              'ipRangeStart': '10.147.17.1'}],
                       'private': 'true',
                       'routes': [{'target': '10.147.17.0/24', 'via': None}],
                       'v4AssignMode': {'zt': 'true'}}}

    response = session.post(url=url, json=data)
    ZEROTIER_NW_ID = response.json()['id']
    print(ZEROTIER_NW_ID)
    file_ZT = open('ZT_NET_ID', 'w')
    file_ZT.write(ZEROTIER_NW_ID)
    file_ZT.close()
    return ZEROTIER_NW_ID


if __name__ == '__main__':
    action = sys.argv[1]
    token = sys.argv[2]
    manager = packet.Manager(auth_token=token)
    if action == 'delete':
        print(' [*] Deleting the g8os machines ..')
        file_node = open('ZT_HOSTS', 'r')
        hosts = file_node.read().split('\n')[:-1]
        for hostname in hosts:
            print(' [*] Delete %s machine ' % hostname)
            delete_devices(manager, hostname)
    else:
        CORE_0_BRANCH = sys.argv[6]
        zt_token = sys.argv[3]
        itsyouonline_org = sys.argv[4]
        command = 'git ls-remote --heads https://github.com/zero-os/0-core.git {} | wc -l'.format(CORE_0_BRANCH)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        flag = str(process.communicate()[0], 'utf-8').strip('\n')
        zt_net_id = create_zerotire_nw(zt_token=zt_token)
        if flag != '1':
            CORE_0_BRANCH = 'master'

        file_node = open('ZT_HOSTS', 'w')
        for i in range(6):
            hostname = create_pkt_machine(manager, zt_net_id, itsyouonline_org, branch=CORE_0_BRANCH)
            file_node.write(hostname)
            file_node.write('\n')
        file_node.close()
