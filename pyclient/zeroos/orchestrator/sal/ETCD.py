from io import BytesIO
import logging
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETCD:
    """etced server"""

    def __init__(self, name, container, serverBind, clientBind, peers, data_dir='/mnt/data'):
        self.name = name
        self.container = container
        self.serverBind = serverBind
        self.clientBind = clientBind
        self.data_dir = data_dir
        self.peers = ",".join(peers)
        self._ays = None

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
