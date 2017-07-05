from js9 import j
from .StorageEngine import StorageEngine

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageCluster:
    """StorageCluster is a cluster of StorageEngine servers"""

    def __init__(self, label, nodes=None, disk_type=None):
        """
        @param label: string repsenting the name of the storage cluster
        """
        self.label = label
        self.name = label
        self.nodes = nodes or []
        self.filesystems = []
        self.storage_servers = []
        self.disk_type = disk_type
        self.k = 0
        self.m = 0
        self._ays = None

    @classmethod
    def from_ays(cls, service, password):
        logger.debug("load cluster storage cluster from service (%s)", service)
        disk_type = str(service.model.data.diskType)

        nodes = []
        storage_servers = []
        for storageEngine_service in service.producers.get('storage_engine', []):
            storages_server = StorageServer.from_ays(storageEngine_service, password)
            storage_servers.append(storages_server)
            if storages_server.node not in nodes:
                nodes.append(storages_server.node)

        cluster = cls(label=service.name, nodes=nodes, disk_type=disk_type)
        cluster.storage_servers = storage_servers
        cluster.k = service.model.data.k
        cluster.m = service.model.data.m
        return cluster

    def get_config(self):
        data = {'dataStorage': [],
                'metadataStorage': None,
                'label': self.name,
                'status': 'ready' if self.is_running() else 'error',
                'nodes': [node.name for node in self.nodes]}
        for storageserver in self.storage_servers:
            if 'metadata' in storageserver.name:
                data['metadataStorage'] = {'address': storageserver.storageEngine.bind}
            else:
                data['dataStorage'].append({'address': storageserver.storageEngine.bind})
        return data

    @property
    def nr_server(self):
        """
        Number of storage server part of this cluster
        """
        return len(self.storage_servers)

    def find_disks(self):
        """
        return a list of disk that are not used by storage pool
        or has a different type as the one required for this cluster
        """
        logger.debug("find available_disks")
        cluster_name = 'sp_cluster_{}'.format(self.label)
        available_disks = {}

        def check_partition(disk):
            for partition in disk.partitions:
                for filesystem in partition.filesystems:
                    if filesystem['label'].startswith(cluster_name):
                        return True

        for node in self.nodes:
            for disk in node.disks.list():
                # skip disks of wrong type
                if disk.type.name != self.disk_type:
                    continue
                # skip devices which have filesystems on the device
                if len(disk.filesystems) > 0:
                    continue

                # include devices which have partitions
                if len(disk.partitions) == 0:
                    available_disks.setdefault(node.name, []).append(disk)
                else:
                    if check_partition(disk):
                        # devices that have partitions with correct label will be in the beginning
                        available_disks.setdefault(node.name, []).insert(0, disk)
        return available_disks

    def start(self):
        logger.debug("start %s", self)
        for server in self.storage_servers:
            server.start()

    def stop(self):
        logger.debug("stop %s", self)
        for server in self.storage_servers:
            server.stop()

    def is_running(self):
        # TODO: Improve this, what about part of server running and part stopped
        for server in self.storage_servers:
            if not server.is_running():
                return False
        return True

    def health(self):
        """
        Return a view of the state all storage server running in this cluster
        example :
        {
        'cluster1_1': {'storageEngine': True, 'container': True},
        'cluster1_2': {'storageEngine': True, 'container': True},
        }
        """
        health = {}
        for server in self.storage_servers:
            running, _ = server.storageEngine.is_running()
            health[server.name] = {
                'storageEngine': running,
                'container': server.container.is_running(),
            }
        return health

    def __str__(self):
        return "StorageCluster <{}>".format(self.label)

    def __repr__(self):
        return str(self)


class StorageServer:
    """StorageEngine servers"""

    def __init__(self, cluster):
        self.cluster = cluster
        self.container = None
        self.storageEngine = None

    @classmethod
    def from_ays(cls, storageEngine_services, password=None):
        storageEngine = StorageEngine.from_ays(storageEngine_services, password)
        storage_server = cls(None)
        storage_server.container = storageEngine.container
        storage_server.storageEngine = storageEngine
        return storage_server

    @property
    def name(self):
        if self.storageEngine:
            return self.storageEngine.name
        return None

    @property
    def node(self):
        if self.container:
            return self.container.node
        return None

    def _find_port(self, start_port=2000):
        while True:
            if j.sal.nettools.tcpPortConnectionTest(self.node.addr, start_port, timeout=2):
                start_port += 1
                continue
            return start_port

    def start(self, timeout=30):
        logger.debug("start %s", self)
        if not self.container.is_running():
            self.container.start()

        ip, port = self.storageEngine.bind.split(":")
        self.storageEngine.bind = '{}:{}'.format(ip, self._find_port(port))
        self.storageEngine.start(timeout=timeout)

    def stop(self, timeout=30):
        logger.debug("stop %s", self)
        self.storageEngine.stop(timeout=timeout)
        self.container.stop()

    def is_running(self):
        container = self.container.is_running()
        storageEngine, _ = self.storageEngine.is_running()
        return (container and storageEngine)

    def __str__(self):
        return "StorageServer <{}>".format(self.container.name)

    def __repr__(self):
        return str(self)
