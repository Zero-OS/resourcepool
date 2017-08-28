import re
from ..healthcheck import HealthCheckRun

descr = """
Monitors if a network bond (if there is one) has both (or more) interfaces properly active.
"""


class NetworkStability(HealthCheckRun):
    def __init__(self, node):
        resource = '/nodes/{}'.format(node.name)
        super().__init__('networkstability', 'Network Stability Check', 'Network', resource)
        self._recpercent = re.compile('.*(?P<percent>\d+)% packet loss$', re.M)
        self._recavg = re.compile('.*min/avg/max = \d+\.\d+\/(?P<avg>\d+\.\d+).*', re.M)
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
            result = job.get()
            if result.state != 'SUCCESS':
                perc = 0
            else:
                match = self._recpercent.search(result.stdout)
                if not match:
                    perc = 0
                else:
                    failpercent = match.group('percent')
                    perc = 100 - int(failpercent)

            if perc < 70:
                self.add_message('{}_ping_perc'.format(node.name), 'ERROR', "Can reach node {} with percentage {}".format(node.name, perc))
            elif perc < 90:
                self.add_message('{}_ping_perc'.format(node.name), 'WARNING', "Can reach node {} with percentage {}".format(node.name, perc))
            else:
                self.add_message('{}_ping_perc'.format(node.name), 'OK', "Can reach node {} with percentage {}".format(node.name, perc))
            if perc == 0:
                self.add_message('{}_ping_rt'.format(node.name), 'ERROR', "Can't reach node {}".format(node.name))
            else:
                match = self._recavg.search(result.stdout)
                if not match:
                    self.add_message('{}_ping_rt'.format(node.name), 'ERROR', "Can't parse ping data for node {}".format(node.name))
                    continue
                rt = float(match.group('avg'))
                if rt > 200:
                    self.add_message('{}_ping_rt'.format(node.name), 'ERROR', "Round-trip time to node {} is {}".format(node.name, rt))
                elif rt > 10:
                    self.add_message('{}_ping_rt'.format(node.name), 'WARNING', "Round-trip time to node {} is {}".format(node.name, rt))
                else:
                    self.add_message('{}_ping_rt'.format(node.name), 'OK', "Round-trip time to node {} is {}".format(node.name, rt))
