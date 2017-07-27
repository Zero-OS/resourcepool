from js9 import j
from ..healthcheck import HealthCheckRun

descr = """
Checks average memory and CPU usage/load. If average per hour is higher than expected an error condition is thrown.

For both memory and CPU usage throws WARNING if more than 80% used and throws ERROR if more than 95% used.

Result will be shown in the "System Load" section of the Grid Portal / Status Overview / Node Status page.
"""


class CPU(HealthCheckRun):
    def __init__(self, node):
        super().__init__()
        self.node = node

        self.result = {
            'id': 'MEMORY',
            'name': 'Memory',
            'resource': '/nodes/{}'.format(node.name),
            'messages': list(),
            'category': 'System Load',
        }

    def run(self):
        total_mem = self.node.client.info.mem()['total']/(1024*1024)
        mem_history = self.node.client.aggregator.query('machine.memory.ram.available').get('machine.memory.ram.available', {}).get('history', {})

        if '3600' not in mem_history:
            self.result['messages'].append({
                'id': '-1',
                'status': 'WARNING',
                'text': 'Average memory load is not collected yet',
            })
        else:
            avg_available_mem = mem_history['3600'][-1]['avg']
            avg_used_mem = total_mem - avg_available_mem
            avg_mem_percent = avg_used_mem/float(total_mem) * 100
            self.result['messages'].append(get_message('memory', avg_mem_percent))




class Memory(HealthCheckRun):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.result = {
            'id': 'CPU',
            'name': 'CPU',
            'resource': '/nodes/{}'.format(node.name),
            'messages': list(),
            'category': 'System Load',
        }

    def run(self):
        cpu_percent = 0
        count = 0
        cpu_usage = self.node.client.aggregator.query('machine.CPU.percent')
        for cpu, data in cpu_usage.items():
            if '3600' not in data['history']:
                continue
            cpu_percent += (data['history']['3600'][-1]['avg'])
            count += 1

        if count == 0:
            self.result['messages'].append({
                'id': '-1',
                'status': 'WARNING',
                'text': 'Average CPU load is not collected yet',
            })
        else:
            cpu_avg = cpu_percent / float(count)
            self.result['messages'].append(get_message('cpu', cpu_avg))


def get_message(type_, percent):
    message = {
        'id': '-1',
        'status': 'OK',
        'text': r'Average %s load during last hour was: %.2f%%' % (type_.upper(), percent),
    }

    if percent > 95:
        message['status'] = 'ERROR'
        message['text'] = r'Average %s load during last hour was too high' % (type_.upper())
    elif percent > 80:
        message['status'] = 'WARNING'
        message['text'] = r'Average %s load during last hour was too high' % (type_.upper())

    return message