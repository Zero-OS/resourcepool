from ..healthcheck import HealthCheckRun
from js9 import j

descr = """
Clean up ssh deamons and tcp services from migration 
"""


class SSHCleanup(HealthCheckRun):
    def __init__(self, node, job):
        resource = '/nodes/{}'.format(node.name)
        super().__init__('ssh-cleanup', 'SSH Cleanup', 'System Load', resource)
        self.node = node
        self.service = job.service
        self.job = job

    def run(self):
        status = 'OK'
        text = 'Migration Cleanup Succesful'
        finished = []
        try:
            for job in self.service.aysrepo.jobsList():
                job_dict = job.to_dict()
                if job_dict['actionName'] == 'processChange' and job_dict['actorName'] == 'vm':
                    if job_dict['state'] == 'running':
                        continue
                    vm = self.service.aysrepo.serviceGet(instance=job_dict['serviceName'], role=job_dict['actorName'])
                    finished.append("ssh.config_%s" % vm.name)
            for proc in self.node.client.process.list():
                for partial in finished:
                    if partial not in proc['cmdline']:
                        continue
                    config_file = proc['cmdline'].split()[-1]
                    port = config_file.split('_')[-1]
                    
                    self.node.client.process.kill(proc['pid'])
                    tcp_name = "tcp_%s_%s" % (self.node.name, port)
                    tcp_service = self.service.aysrepo.serviceGet(role='tcp', instance=tcp_name)
                    j.tools.async.wrappers.sync(tcp_service.executeAction("drop"), context=self.job.context)
                    tcp_service.delete()
                    if self.node.client.filesystem.exists('/tmp'):
                        self.node.client.filesystem.remove(config_file)

        except Exception as e:
            text = "Error happened, Can not clean ssh process "
            status = "ERROR"

        self.add_message(self.id, status, text)