from js9 import j
import os
from zeroos.core0.client.client import Timeout
import json
import hashlib


class HealthCheckRun:
    def __init__(self, id, name, category, resource):
        self.id = id
        self.name = name
        self.category = category
        self._messages = []
        self.resource = resource
        self.stacktrace = ''

    def start(self, *args, **kwargs):
        try:
            self.run(*args, **kwargs)
        except Exception as e:
            eco = j.errorhandler.parsePythonExceptionObject(e)
            self.stacktrace = eco.traceback
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'resource': self.resource,
            'stacktrace': self.stacktrace or '',
            'messages': self._messages
        }

    def add_message(self, id, status, text):
        self._messages.append({'id': id, 'text': text, 'status': status})


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

    def cpu_mem(self):
        from .healthchecks.cpu_mem_core import CPU, Memory
        cpu = CPU(self.node)
        memory = Memory(self.node)
        return [cpu.start(), memory.start()]

    def network_bond(self):
        from .healthchecks.networkbond import NetworkBond
        bond = NetworkBond(self.node)
        return bond.start()

    def node_temperature(self, container):
        from .healthchecks.temperature import Temperature
        temperature = Temperature(self.node)
        result = temperature.start(container)
        return result

    def rotate_logs(self):
        from .healthchecks.log_rotator import RotateLogs
        rotator = RotateLogs(self.node)
        return rotator.start()

    def openfiledescriptors(self):
        from .healthchecks.openfiledescriptors import OpenFileDescriptor
        ofd = OpenFileDescriptor(self.node)
        return ofd.start()

    def interrupts(self):
        from .healthchecks.interrupts import Interrupts
        inter = Interrupts(self.node)
        return inter.start()

    def threads(self):
        from .healthchecks.threads import Threads
        thread = Threads(self.node)
        return thread.start()

    def powersupply(self, container):
        from .healthchecks.powersupply import PowerSupply
        powersupply = PowerSupply(self.node)
        return powersupply.start(container)

    def fan(self, container):
        from .healthchecks.fan import Fan
        fan = Fan(self.node)
        return fan.start(container)

    def context_switch(self):
        from .healthchecks.context_switch import ContextSwitch
        return ContextSwitch(self.node).start()

