from js9 import j

descr = """
Checks average memory and CPU usage/load. If average per hour is higher than expected an error condition is thrown.

For both memory and CPU usage throws WARNING if more than 80% used and throws ERROR if more than 95% used.

Result will be shown in the "System Load" section of the Grid Portal / Status Overview / Node Status page.
"""


def action(node):
    category = 'System Load'
    resource = '/nodes/{}'.format(node.name)
    total_mem = node.client.info.mem()['total']/(1024*1024)
    mem_history = node.client.aggregator.query('machine.memory.ram.available').get('machine.memory.ram.available', {}).get('history', {})

    memory_result = {
        'id': 'MEMORY',
        'name': 'Memory',
        'resource': resource,
        'messages': list(),
        'category': category,
    }
    if '3600' not in mem_history:
        memory_result['messages'].append({
            'id': '-1',
            'status': 'WARNING',
            'text': 'Average memory load is not collected yet',
        })
    else:
        avg_available_mem = mem_history['3600'][-1]['avg']
        avg_used_mem = total_mem - avg_available_mem
        avg_mem_percent = avg_used_mem/float(total_mem) * 100
        memory_result['messages'].append(get_message('memory', avg_mem_percent))

    cpu_percent = 0
    count = 0
    cpu_usage = node.client.aggregator.query('machine.CPU.percent')
    for cpu, data in cpu_usage.items():
        if '3600' not in data['history']:
            continue
        cpu_percent += (data['history']['3600'][-1]['avg'])
        count += 1

    cpu_result = {
        'id': 'CPU',
        'name': 'Cpu',
        'resource': resource,
        'messages': list(),
        'category': category,
    }

    if count == 0:
        cpu_result['messages'].append({
            'id': '-1',
            'status': 'WARNING',
            'text': 'Average CPU load is not collected yet',
        })
    else:
        cpu_avg = cpu_percent / float(count)
        cpu_result['messages'].append(get_message('cpu', cpu_avg))

    return [memory_result, cpu_result]


def get_message(type_, percent):
    level = None
    message = {
        'id': '-1',
        'status': 'OK',
        'text': r'Average %s load during last hour was: %.2f%%' % (type_.upper(), percent),
    }

    if percent > 95:
        level = 1
        message['status'] = 'ERROR'
        message['text'] = r'Average %s load during last hour was too high' % (type_.upper())
    elif percent > 80:
        level = 2
        message['status'] = 'WARNING'
        message['text'] = r'Average %s load during last hour was too high' % (type_.upper())
    if level:
        msg = 'Average %s load during last hour was above threshold value: %.2f%%' % (type_.upper(), percent)
        eco = j.errorconditionhandler.getErrorConditionObject(
            msg=msg, category='monitoring', level=level, type='OPERATIONS')
        eco.nid = j.application.whoAmI.nid
        eco.gid = j.application.whoAmI.gid
        eco.process()

    return message


if __name__ == '__main__':
    import yaml
    print(yaml.dump(action(), default_flow_style=False))
