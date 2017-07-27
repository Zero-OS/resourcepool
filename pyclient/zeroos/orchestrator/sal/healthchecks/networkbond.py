import re
from ..healthcheck import HealthCheckRun

descr = """
Monitors if a network bond (if there is one) has both (or more) interfaces properly active.
"""


class NetworkBond(HealthCheckRun):
    def __init__(self):
        super(self).__init__()
        self.result['id'] = 'networkbond'
        self.result['name'] = 'Network Bond Check'
        self.result['category'] = 'Hardware'

    def run(self, node):
        self.result['resource'] = '/nodes/{}'.format(node.name)
        ovs = "{}_ovs".format(node.name)
        try:
            container = node.containers.get(ovs)
        except LookupError:
            # no ovs configured nothing to report on
            return
        jobresult = container.client.system('ovs-appctl bond/show').get()
        if jobresult.state == 'ERROR':
            return
        output = jobresult.stdout
        bonds = []
        bond = {}
        for match in re.finditer('(?:---- bond-(?P<bondname>\w+) ----)?.+?\n(?:slave (?:(?P<slavename>\w+): (?P<state>\w+)))', output, re.DOTALL):
            groups = match.groupdict()
            slave = {'name': groups['slavename'], 'state': groups['state']}
            if groups['bondname']:
                if bond:
                    bonds.append(bond)
                bond = {'name': groups['bondname']}
            bond.setdefault('slaves', []).append(slave)
        if bond:
            bonds.append(bond)

        for bond in bonds:
            badslaves = []
            for slave in bond['slaves']:
                if slave['state'] != 'enabled':
                    badslaves.append(slave['name'])
            state = 'OK'
            if badslaves:
                msg = 'Bond: {} has problems with slaves {}'.format(bond['name'], ', '.join(badslaves))
                state = 'ERROR' if len(badslaves) == len(bond['slaves']) else 'WARNING'
            else:
                msg = 'Bond: {}, all slave are ok'.format(bond['name'])

            message = {'text': msg, 'id': bond, 'status': state}
            self.result['messages'].append(message)
