import psutil


descr = """
Check open file descriptors for each node process, if it exceeds 90% of the soft limit, it raises a warning,
if it exceeds 90% of the hard limit, it raises an error.
"""


def action(node):
    result = {
        'id': 'OPENFILEDESCRIPTORS',
        'name': 'Open File Descriptors',
        'resource': '/nodes/{}'.format(node.name),
        'category': 'System Load',
        'messages': list(),
    }

    for process in node.client.process.list():
        for rlimit in process['rlimit']:
            if rlimit['resource'] == psutil.RLIMIT_NOFILE:
                pid = str(process['pid'])
                if (0.9 * rlimit['soft']) <= process['ofd'] < (0.9 * rlimit['hard']):
                    message = {
                        'id': pid,
                        'status': 'WARNING',
                        'text': 'Open file descriptors for process %s exceeded 90%% of the soft limit' % pid,
                    }
                    result['messages'].append(message)
                elif process['ofd'] >= (0.9 * rlimit['hard']):
                    result['status'] = 'ERROR'
                    result['message'] = 'Open file descriptors for process %s exceeded 90%% of the hard limit' % pid
                    message = {
                        'id': pid,
                        'status': 'ERROR',
                        'text': 'Open file descriptors for process %s exceeded 90%% of the hard limit' % pid,
                    }
                    result['messages'].append(message)
                break

    if not result['messages']:
        result['messages'] = [{
            'id': '-1',
            'status': 'OK',
            'text': 'Open file descriptors for all processes are within limit',
        }]
    return [result]


if __name__ == '__main__':
    action()
