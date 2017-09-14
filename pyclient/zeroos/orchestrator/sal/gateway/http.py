from zeroos.orchestrator.sal import templates
import signal
import time


class HTTPServer:
    def __init__(self, container, type, httpproxies):
        self.container = container
        self.type = type
        self.httpproxies = httpproxies

    def id(self):
        return 'caddy-{}.{}'.format(self.type, self.container.name)

    def apply_rules(self):
        # caddy
        caddyconfig = templates.render('caddy.conf', type=self.type, httpproxies=self.httpproxies).strip()
        conf = '/etc/caddy-{}.conf'.format(self.type)
        self.container.upload_content(conf, caddyconfig)
        self.container.client.job.kill(self.id(), int(signal.SIGUSR1))
        if caddyconfig == '':
            return
        self.container.client.system(
            'caddy -agree -conf {}'.format(conf), stdin='\n', id=self.id())
        start = time.time()
        while start + 10 > time.time():
            if self.is_running():
                return True
            time.sleep(0.5)
        raise RuntimeError("Failed to start caddy server")

    def is_running(self):
        try:
            self.container.client.job.list(self.id())
        except:
            return False
        portnr = 80 if self.type == 'http' else 443
        for port in self.container.client.info.port():
            if port['network'] .startswith('tcp') and port['port'] == portnr:
                return True
        return False
