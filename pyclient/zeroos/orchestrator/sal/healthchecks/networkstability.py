import re
from ..healthcheck import HealthCheckRun

descr = """
Monitors if a network bond (if there is one) has both (or more) interfaces properly active.
"""


class NetworkStability(HealthCheckRun):
    def __init__(self, node):
        resource = '/nodes/{}'.format(node.name)
        super().__init__('networkstability', 'Network Stability Check', 'Network',resource)
        self.node = node

    def run(self, nodes):
        nic = self.node.get_nic_by_ip(self.node.addr)
        if nic is None:
            raise LookupError("Couldn't get the management nic")
        jobs = []
        for node in nodes:
            other_nic = node.get_nic_by_ip(node.addr)
            if other_nic is not None:
                if nic['mtu'] != other_nic['mtu']:
                    self.add_message('{}_mtu'.format(node.name), 'ERROR', 'The management interface has mtu {} which is different than node {} which is {}'.format(nic['mtu'], node.name, other_nic['mtu']))
                else:
                    self.add_message('{}_mtu'.format(node.name), 'OK', 'The management interface has mtu {} is the same as node {}'.format(nic['mtu'], node.name, other_nic['mtu']))
            else:
                self.add_message('{}_mtu'.format(node.name), 'ERROR', "Couldn't get the management nic for node {}".format(node.name))
            jobs.append(self.node.client.system('ping -I {} -c 10 -W 1 -q {}'.format(self.node.addr, node.addr), max_time=20))
        for node, job in zip(nodes, jobs):
            res = job.get().stdout.split('\n')
            perc = 100 - int(res[2].split(',')[-1].strip().split()[0][:-1])
            if perc < 70:
                self.add_message('{}_ping_perc'.format(node.name), 'ERROR', "Can reach node {} with percentage {}".format(node.name, perc))
            elif perc < 90:
                self.add_message('{}_ping_perc'.format(node.name), 'WARNING', "Can reach node {} with percentage {}".format(node.name, perc))
            else:
                self.add_message('{}_ping_perc'.format(node.name), 'OK', "Can reach node {} with percentage {}".format(node.name, perc))
            if perc == 0:
                self.add_message('{}_ping_rt'.format(node.name), 'ERROR', "Can't reach node {}".format(node.name))
            else:
                rt = float(res[3].split('/')[3])
                if rt > 200:
                    self.add_message('{}_ping_rt'.format(node.name), 'ERROR', "Round-trip time to node {} is {}".format(node.name, rt))
                elif rt > 10:
                    self.add_message('{}_ping_rt'.format(node.name), 'WARNING', "Round-trip time to node {} is {}".format(node.name, rt))
                else:
                    self.add_message('{}_ping_rt'.format(node.name), 'OK', "Round-trip time to node {} is {}".format(node.name, rt))
