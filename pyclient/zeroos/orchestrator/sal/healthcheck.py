from js9 import j
import os
from zeroos.core0.client.client import Timeout
import json
import hashlib


class HealthCheckRun:
    def __init__(self):
        self.result = {
            'id': '',
            'name': '',
            'resource': '',
            'category': '',
            'stacktrace': '',
            'messages': list(),
        }

    def start(self, *args, **kwargs):
        try:
            self.run(*args, **kwargs)
        except Exception as e:
            eco = j.errorhandler.parsePythonExceptionObject(e)
            self.result['stacktrace'] = eco.traceback
        return self.result


class ContainerContext:
    def __init__(self, node, flist):
        self.node = node
        self.flist = flist
        self.container = None
        self._name = 'healthcheck_{}'.format(hashlib.md5(flist.encode()).hexdigest())

    def __enter__(self):
        try:
            self.container = self.node.containers.get(self._name)
        except LookupError:
            self.container = self.node.containers.create(self._name, self.flist, host_network=True, privileged=True)
        return self.container

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


class HealthCheck:
    def __init__(self, node):
        self.node = node
        self.healtcheckfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'healthchecks')

    def with_container(self, flist):
        return ContainerContext(self.node, flist)

    def run(self, container, name, timeout=None):
        try:
            healthcheckfile = os.path.join(self.healtcheckfolder, name + '.py')
            if not os.path.exists(healthcheckfile):
                raise RuntimeError("Healtcheck with name {} not found".format(name))
            container.client.filesystem.upload_file('/tmp/{}.py'.format(name), healthcheckfile)
            try:
                job = container.client.bash('python3 /tmp/{}.py'.format(name))
                response = job.get(timeout)
            except Timeout:
                container.client.job.kill(job.id, 9)
                raise RuntimeError("Failed to execute {} on time".format(name))
            if response.state == 'ERROR':
                raise RuntimeError("Failed to execute {} {}".format(name, response.stdout))
            try:
                return json.loads(response.stdout)
            except Exception:
                raise RuntimeError("Failed to parse response of {}".format(name))
        except Exception as e:
            healtcheck = {
                'id': name,
                'status': 'ERROR',
                'message': str(e)
            }
            return healtcheck

    def calc_cpu_mem(self):
        from .healthchecks.cpu_mem_core_check import action

        return action(self.node)

    def network_bond(self):
        from .healthchecks.networkbond import NetworkBond
        bond = NetworkBond()
        return bond.start(self.node)

    def rotate_logs(self):
        from .healthchecks.log_rotator import action

        return action(self.node)

    def check_ofd(self):
        from .healthchecks.openfiledescriptors import action

        return action(self.node)
