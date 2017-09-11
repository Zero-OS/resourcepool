from io import BytesIO
import logging
import yaml
import etcd3

logging.basicConfig(level=logging.INFO)
default_logger = logging.getLogger(__name__)


class EtcdCluster:
    """etced server"""

    def __init__(self, name, dialstrings, mgmtdialstrings, logger=None):
        self.name = name
        self.dialstrings = dialstrings
        self.mgmtdialstrings = mgmtdialstrings
        self._ays = None
        self.logger = default_logger
        if logger:
            self.logger = logger

    @classmethod
    def from_ays(cls, service, password=None, logger=None):
        if not logger:
            logger = default_logger
        logger.debug("create storageEngine from service (%s)", service)

        dialstrings = set()
        for etcd_service in service.producers.get('etcd', []):
            etcd = ETCD.from_ays(etcd_service, password)
            dialstrings.add(etcd.clientBind)

        mgmtdialstrings = set()
        for etcd_service in service.producers.get('etcd', []):
            etcd = ETCD.from_ays(etcd_service, password)
            mgmtdialstrings.add(etcd.mgmtClientBind)

        return cls(
            name=service.name,
            dialstrings=",".join(dialstrings),
            mgmtdialstrings=",".join(mgmtdialstrings),
            logger=logger
        )

    def put(self, key, value):
        dialstrings = self.mgmtdialstrings.split(",")
        for dialstring in dialstrings:
            host, port = dialstring.split(":")
            try:
                etcd = etcd3.client(host=host, port=port)
                etcd.put(key, value)
                break
            except (etcd3.exceptions.ConnectionFailedError, etcd3.exceptions.ConnectionTimeoutError) as e:
                self.logger.error("Could not connect to etcd on %s:%s" % (host, port))
        else:
            raise RuntimeError("etcd cluster %s has now running etcd servers" % self.name)


class ETCD:
    """etced server"""

    def __init__(self, name, container, serverBind, clientBind, peers, mgmtClientBind, data_dir='/mnt/data',
                 password=None, logger=None):
        self.name = name
        self.container = container
        self.serverBind = serverBind
        self.clientBind = clientBind
        self.mgmtClientBind = mgmtClientBind
        self.data_dir = data_dir
        self.peers = ",".join(peers)
        self._ays = None
        self._password = None
        self.logger = default_logger
        if logger:
            self.logger = logger

    @classmethod
    def from_ays(cls, service, password=None, logger=None):
        if not logger:
            logger = default_logger
        logger.debug("create storageEngine from service (%s)", service)
        from .Container import Container
        container = Container.from_ays(service.parent, password, logger=service.logger)

        return cls(
            name=service.name,
            container=container,
            serverBind=service.model.data.serverBind,
            clientBind=service.model.data.clientBind,
            mgmtClientBind=service.model.data.mgmtClientBind,
            data_dir=service.model.data.homeDir,
            peers=service.model.data.peers,
            password=password,
            logger=logger
        )

    def start(self):
        configpath = "/etc/etcd_{}.config".format(self.name)

        client_urls = ",".join(list({"http://{}".format(self.clientBind), "http://{}".format(self.mgmtClientBind)}))
        config = {
            "name": self.name,
            "initial-advertise-peer-urls": "http://{}".format(self.serverBind),
            "listen-peer-urls": "http://{}".format(self.serverBind),
            "listen-client-urls": client_urls,
            "advertise-client-urls": client_urls,
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

    def stop(self):
        import time
        jobID = "etcd.{}".format(self.name)
        self.container.client.job.kill(jobID)
        start = time.time()
        while start + 15 > time.time():
            time.sleep(1)
            try:
                self.container.client.job.list(jobID)
            except RuntimeError:
                return
            continue

        raise RuntimeError('failed to stop etcd.')

    def put(self, key, value):
        if value.startswith("-"):
            value = "-- %s" % value
        if key.startswith("-"):
            key = "-- %s" % key
        cmd = '/bin/etcdctl \
          --endpoints {etcd} \
          put {key} "{value}"'.format(etcd=self.clientBind, key=key, value=value)
        return self.container.client.system(cmd, env={"ETCDCTL_API": "3"}).get()
