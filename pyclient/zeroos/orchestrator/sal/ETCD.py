from io import BytesIO
import logging
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EtcdCluster:
    """etced server"""

    def __init__(self, name, dialstrings):
        self.name = name
        self.dialstrings = dialstrings
        self._ays = None

    @classmethod
    def from_ays(cls, service, password=None):
        logger.debug("create storageEngine from service (%s)", service)

        dialstrings = set()
        for etcd_service in service.producers.get('etcd', []):
            etcd = ETCD.from_ays(etcd_service, password)
            dialstrings.add(etcd.clientBind)

        return cls(
            name=service.name,
            dialstrings=",".join(dialstrings),
        )


class ETCD:
    """etced server"""

    def __init__(self, name, container, serverBind, clientBind, peers, data_dir='/mnt/data', password=None):
        self.name = name
        self.container = container
        self.serverBind = serverBind
        self.clientBind = clientBind
        self.data_dir = data_dir
        self.peers = ",".join(peers)
        self._ays = None
        self._password = None

    @classmethod
    def from_ays(cls, service, password=None):
        logger.debug("create storageEngine from service (%s)", service)
        from .Container import Container
        container = Container.from_ays(service.parent, password)

        return cls(
            name=service.name,
            container=container,
            serverBind=service.model.data.serverBind,
            clientBind=service.model.data.clientBind,
            data_dir=service.model.data.homeDir,
            peers=service.model.data.peers,
            password=password
        )

    def start(self):
        configpath = "/etc/etcd_{}.config".format(self.name)

        config = {
            "name": self.name,
            "initial-advertise-peer-urls": "http://{}".format(self.serverBind),
            "listen-peer-urls": "http://{}".format(self.serverBind),
            "listen-client-urls": "http://{}".format(self.clientBind),
            "advertise-client-urls": "http://{}".format(self.clientBind),
            "initial-cluster": self.peers,
            "data-dir": self.data_dir,
            "initial-cluster-state": "new"
        }
        yamlconfig = yaml.safe_dump(config, default_flow_style=False)
        configstream = BytesIO(yamlconfig.encode('utf8'))
        configstream.seek(0)
        self.container.client.filesystem.upload(configpath, configstream)
        cmd = '/bin/etcd --config-file %s' % configpath
        self.container.client.system(cmd, id="etcd.{}".format(self.name))
        if not self.container.is_port_listening(int(self.serverBind.split(":")[1])):
            raise RuntimeError('Failed to start etcd server: {}'.format(self.name))

    def put(self, key, value):
        if value.startswith("-"):
            value = "-- %s" % value
        if key.startswith("-"):
            key = "-- %s" % key
        cmd = '/bin/etcdctl \
          --endpoints {etcd} \
          put {key} "{value}"'.format(etcd=self.clientBind, key=key, value=value)
        return self.container.client.system(cmd, env={"ETCDCTL_API": "3"}).get()


    def recover(self, backup_dir, old_container, new_container):
        from .Node import Node
        from Container import Container
        
        # client for new node and for new conainer and root path of that container
        new_container_node = Node.from_ays(new_container.parent, password=self._password)
        new_container_client = Container.from_ays(new_container, password=self._password)
        new_container_path = new_container_node.container.list()[new_container_client.container]['container']['arguments']['root']

        # client for old node and root path to old container
        old_container_node = Node.from_ays(old_container.parent, password=self._password)        
        old_container_path = old_container_node.container.list()[self.container.container]['container']['arguments']['root']
        
        self.container.client.system("/bin/etcdctl backup --data-dir %s --backup-dir %s " % (self.data_dir, 
                                                                                             backupdir)).get()

        def walk(root):
            for path in self.container.client.filesystem.list(root):
                full_path = "%s/%s" % (root, path)
                if not path['is_dir']:
                    new_container_node.client.filesystem.move("%s/%s" % (old_container_path, full_path),
                                                              "%s/%s" % (new_container_path, self.data_dir))
                    continue
                new_container_node.client.filesystem.mkdir(full_path)
                walk(full_path)

        walk(self.data_dir)
        return