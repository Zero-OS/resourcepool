#!/usr/bin/python3
from random import randint
import packet
import time
import os
import sys
import threading
import subprocess
import configparser


def create_new_device(manager, hostname, zt_net_id, itsyouonline_org, branch='master'):
    project = manager.list_projects()[0]
    ipxe_script_url = 'https://bootstrap.gig.tech/ipxe/{}/{}/organization={}'.format(branch, zt_net_id, itsyouonline_org)
    print('creating new machine: {}  .. '.format(hostname))
    device = manager.create_device(project_id=project.id,
                                   hostname=hostname,
                                   plan='baremetal_2',
                                   operating_system='custom_ipxe',
                                   ipxe_script_url=ipxe_script_url,
                                   facility='ams1')
    return device


def delete_devices(manager):
    config = configparser.ConfigParser()
    config.read('api_testing/config.ini')
    machines = config['main']['0_core_machines']
    
    if machines:
        machines = machines.split(',')
        project = manager.list_projects()[0]
        devices = manager.list_devices(project.id)
        for hostname in machines:
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
        print('device hasn\'t been created')
        raise

    print('provisioning the new machine ..')
    while True:
        dev = manager.get_device(device.id)
        if dev.state == 'active':
            break
    time.sleep(5)

    config = configparser.ConfigParser()
    config.read('api_testing/config.ini')
    config['main']['target_ip'] = dev.ip_addresses[0]['address']
    old_hosts =  config['main']['0_core_machines']
    if old_hosts:
        config['main']['0_core_machines'] = old_hosts + ',' + hostname
    else:
        config['main']['0_core_machines'] = hostname
    with open('api_testing/config.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    action = sys.argv[1]
    token = sys.argv[2]
    manager = packet.Manager(auth_token=token)
    branch = 'master'
    if action == 'delete':
        print('deleting the g8os machines ..')
        delete_devices(manager)
    else:
        zt_net_id = sys.argv[3]
        itsyouonline_org = sys.argv[4]
        branch = sys.argv[5]
        command='git ls-remote --heads https://github.com/zero-os/0-core.git {} | wc -l'.format(branch)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        flag=str(process.communicate()[0], 'utf-8').strip('\n')
        if flag != '1':
           branch = 'master'
        threads = []
        for i in range(2):
            thread = threading.Thread(target=create_pkt_machine, args=(manager, zt_net_id, itsyouonline_org), kwargs={'branch': '{}'.format(branch)})
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()
