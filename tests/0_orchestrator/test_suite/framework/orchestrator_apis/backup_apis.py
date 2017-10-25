from framework.orchestrator_apis import *
from framework.orchestrator_base import OrchestratorBase


class BackupAPI(OrchestratorBase):
    def __init__(self, orchestrator_driver):
        self.orchestrator_driver = orchestrator_driver
        self.orchestrator_client = self.orchestrator_driver.orchestrator_client

    @catch_exception_decoration
    def list_backups(self):
        return self.orchestrator_client.backup.ListBackup()

    @catch_exception_decoration
    def post_container_backups(self, container_name, url, **kwargs):
        data = {"name": self.random_string(),
                "container": container_name,
                "url": url}
        data = self.update_default_data(default_data=data, new_data=kwargs)
        return self.orchestrator_client.backup.BackupContainer(data=data)
