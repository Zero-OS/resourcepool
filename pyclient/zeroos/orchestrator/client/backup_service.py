class BackupService:
    def __init__(self, client):
        self.client = client



    def ListBackup(self, headers=None, query_params=None, content_type="application/json"):
        """
        List backups
        It is method for GET /backup
        """
        uri = self.client.base_url + "/backup"
        return self.client.get(uri, None, headers, query_params, content_type)


    def BackupContainer(self, data, headers=None, query_params=None, content_type="application/json"):
        """
        Backup a container
        It is method for POST /backup
        """
        uri = self.client.base_url + "/backup"
        return self.client.post(uri, data, headers, query_params, content_type)
