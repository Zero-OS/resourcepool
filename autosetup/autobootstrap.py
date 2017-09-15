#!/usr/bin/python3
import argparse
import subprocess
import requests
import sys
import time
import yaml
import pytoml as toml
from urllib.parse import urlparse
from zeroos.orchestrator.sal.Node import Node

class OrchestratorSSHTools:
    def __init__(self):
        pass

    def localkeys(self):
        """
        returns local ssh public keys available and loaded
        """
        process = subprocess.run(["ssh-add", "-L"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # avoid empty agent
        if process.returncode != 0:
            return ""

        return process.stdout

    def loadkey(self, filename):
        with open(filename, "r") as f:
            sshkey = f.read()

        return sshkey

    def validkey(self, key):
        return key.startswith("-----BEGIN RSA PRIVATE KEY-----")

    def encryptedkey(self, key):
        # this is not enough for new version but already a good point
        return (",ENCRYPTED" in key)

class OrchestratorInstallerTools:
    def __init__(self):
        self.ssh = OrchestratorSSHTools()

    def generatetoken(self, clientid, clientsecret, organization=None, validity=None):
        params = {
            'grant_type': 'client_credentials',
            'client_id': clientid,
            'client_secret': clientsecret,
            'response_type': 'id_token',
            'scope': 'offline_access'
        }

        if validity:
            params['validity'] = validity

        if organization:
            params['scope'] = 'user:memberof:%s,offline_access' % organization

        url = 'https://itsyou.online/v1/oauth/access_token'
        resp = requests.post(url, params=params)
        resp.raise_for_status()

        return resp.content.decode('utf8')

    def ztstatus(self, cn, macaddr):
        """
        Return a zerotier node object from a mac address
        """
        ztinfo = cn.client.zerotier.list()
        for zt in ztinfo:
            if zt['mac'] == macaddr:
                    return zt

        return None

    def ztwait(self, cn, macaddr):
        notified = False

        while True:
            # get and ensure mac address is there
            status = self.ztstatus(cn, macaddr)
            if not status:
                return None

            if not notified:
                notified = True
                print("[+] waiting zerotier access (id: %s, hardware: %s)" % (status['nwid'], status['mac']))
                self.progress()

            if len(status['assignedAddresses']) == 0:
                self.progressing()
                time.sleep(1)
                continue

            # network ready, address set
            self.progressing(True)
            return status['assignedAddresses'][0].split('/')[0]

    def containerzt(self, cn):
        # for all zerotier network, waiting for a valid address
        ztinfo = cn.client.zerotier.list()

        for ztnet in ztinfo:
            self.ztwait(cn, ztnet['mac'])


    def progress(self):
        self.xprint("[+] ")

    def progressing(self, final=False):
        progression = "."
        if final:
            progression = " done\n"

        self.xprint(progression)

    def xprint(self, content):
        sys.stdout.write(content)
        sys.stdout.flush()

    def hostof(self, upstream):
        # attempt ssh/url style
        url = urlparse(upstream)
        if url.hostname is not None:
            return {"host": url.hostname, "port": url.port}

        # fallback to git style

        # git@github.com:repository
        # -> ['git', 'github.com:repository']
        #        -> ['github.com', 'repository']
        hostname = upstream.split("@")[1].split(":")[0]
        return {"host": hostname, "port": 22}

    def waitsfor(self, cn, command):
        self.progress()

        while True:
            self.progressing()
            x = cn.client.bash(command).get()

            if x.state == 'SUCCESS':
                self.progressing(True)
                return True

        # waits until it's not done

class OrchestratorInstaller:
    def __init__(self):
        self.tools = OrchestratorInstallerTools()

        self.node = None
        self.flist = "https://hub.gig.tech/maxux/0-orchestrator-full-alpha-8.flist"
        self.ctname = None
        self.core_version = "master"
        self.templates = "/opt/code/github/zero-os/0-orchestrator/autosetup/templates"

    def connector(self, remote, auth):
        """
        remote: remote address of the node
        auth: password (jwt token usualy) nfor client
        """
        print("[+] contacting zero-os server: %s" % remote)
        while True:
            try:
                node = Node(remote, password=auth)
                node.client.timeout = 180
                break

            except RuntimeError as e:
                print("[-] cannot connect server (make sure the server is reachable), retrying")
                time.sleep(1)
                pass

        self.node = node

        return node

    def prepare(self, ctname, ztnetwork, ztnetnodes, sshkey):
        """
        node: connected node object
        ctname: container name
        ztnetwork: zerotier network the container should join
        """
        self.ctname = ctname

        print("[+] starting orchestrator container")
        network = [
            {'type': 'default'},
            {'type': 'zerotier', 'id': ztnetwork}
        ]

        if ztnetnodes != ztnetwork:
            network.append({'type': 'zerotier', 'id': ztnetnodes})

        env = {
            "PATH": "/opt/jumpscale9/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "PYTHONPATH": "/opt/jumpscale9/lib/:/opt/code/github/jumpscale/core9/:/opt/code/github/jumpscale/prefab9/:/opt/code/github/jumpscale/ays9:/opt/code/github/jumpscale/lib9:/opt/code/github/jumpscale/portal9",
            "HOME": "/root",
            "LC_ALL": "C.UTF-8",
            "LC_LANG": "UTF-8"
        }

        hostvolume = '/var/cache/containers/orchestrator-%s' % ctname

        if not self.node.client.filesystem.exists(hostvolume):
            self.node.client.filesystem.mkdir(hostvolume)

        cn = self.node.containers.create(
            name=ctname,
            flist=self.flist,
            nics=network,
            hostname='bootstrap',
            mounts={hostvolume: '/optvar'},
            env=env
        )

        print("[+] setting up and starting ssh server")
        cn.client.bash('dpkg-reconfigure openssh-server').get()
        cn.client.bash('/etc/init.d/ssh start').get()

        print("[+] allowing local ssh key")
        localkeys = self.tools.ssh.localkeys()
        if localkeys != "":
            fd = cn.client.filesystem.open("/root/.ssh/authorized_keys", "w")
            cn.client.filesystem.write(fd, localkeys)
            cn.client.filesystem.close(fd)

        else:
            print("[-] warning: no local ssh public key found, nothing added")

        # make sure the enviroment is also set in bashrc for when ssh is used
        print("[+] setting environment variables")
        fd = cn.client.filesystem.open("/root/.bashrc", "a")
        for k, v in env.items():
            export = "export %s=%s\n" % (k, v)
            cn.client.filesystem.write(fd, export.encode('utf-8'))
        cn.client.filesystem.close(fd)

        print("[+] configuring zerotier access")
        containeraddr = self.tools.containerzt(cn)

        if sshkey:
            print("[+] writing ssh private key")
            fd = cn.client.filesystem.open("/root/.ssh/id_rsa", "w")
            cn.client.filesystem.write(fd, sshkey.encode('utf-8'))
            cn.client.filesystem.close(fd)

            # extracting public key from private key
            cn.client.bash("chmod 0600 /root/.ssh/id_rsa").get()
            cn.client.bash("ssh-keygen -y -f /root/.ssh/id_rsa > /root/.ssh/id_rsa.pub").get()

        else:
            print("[+] no private ssh key provided, generating new keys")
            cn.client.bash("ssh-keygen -f /root/.ssh/id_rsa -t rsa -N ''").get()

        publickey = cn.client.bash("cat /root/.ssh/id_rsa.pub").get()

        return {'address': containeraddr, 'publickey': publickey.stdout.strip()}

    def configure(self, upstream, email, organization=None):
        """
        upstream: git upstream address of orchestrator repository
        email: email address used for git and caddy certificates
        organization: organization name ays should join
        """
        print("[+] configuring services")
        cn = self.node.containers.get(self.ctname)

        if organization:
            print("[+] setting organization")
            if not cn.client.filesystem.exists("/optvar/cfg"):
                cn.client.filesystem.mkdir("/optvar/cfg")

            source = cn.client.bash("cat /optvar/cfg/jumpscale9.toml").get()
            config = toml.loads(source.stdout)

            config['ays'] = {
                'production': True,
                'oauth': {
                    'jwt_key': "MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n27MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny66+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv",
                    'organization': organization,
                }
            }

            fd = cn.client.filesystem.open("/optvar/cfg/jumpscale9.toml", "w")
            cn.client.filesystem.write(fd, toml.dumps(config).encode('utf-8'))
            cn.client.filesystem.close(fd)

        print("[+] configuring git client")
        cn.client.bash("git config --global user.name 'AYS System'").get()
        cn.client.bash("git config --global user.email '%s'" % email).get()

        print("[+] preparing upstream repository")
        cn.client.filesystem.mkdir("/optvar/cockpit_repos")

        host = self.tools.hostof(upstream)
        print("[+] authorizing %s (port: %d)" % (host['host'], host['port']))
        cn.client.bash("ssh-keyscan -p %d %s >> ~/.ssh/known_hosts" % (host['port'], host['host'])).get()

        print("[+] cloning upstream repository")
        print("[+] (please ensure the host have access (allows public key ?) to upstream repository)")
        self.tools.waitsfor(cn, "git clone %s /tmp/upstream" % upstream)

        resp = cn.client.bash("cd /tmp/upstream && git rev-parse HEAD").get()

        print("[+] configuring upstream repository")
        repository = "/optvar/cockpit_repos/orchestrator-server"

        # upstream is empty, let create a new repository
        if resp.code != 0:
            print("[+] git repository is empty, creating empty repository")
            cn.client.bash("cd /tmp/upstream/ && git init").get()
            cn.client.bash("cd /tmp/upstream/ && git remote add origin %s" % upstream).get()

        print("[+] ensure ays repository default layout")
        for directory in ["services", "actorTemplates", "actors", "blueprints"]:
            target = "/tmp/upstream/%s" % directory

            if not cn.client.filesystem.exists(target):
                cn.client.bash("mkdir -p %s && touch %s/.keep" % (target, target)).get()

        print("[+] commit initialization changes")
        cn.client.bash("touch /tmp/upstream/.ays").get()
        cn.client.bash("cd /tmp/upstream/ && git add .").get()
        cn.client.bash("cd /tmp/upstream/ && git commit -m 'Initial ays commit'").get()

        print("[+] moving to orchestrator repository")
        # moving upstream to target cockpit repository, removing any previous one
        cn.client.bash("rm -rf %s" % repository).get()
        cn.client.bash("mv /tmp/upstream %s" % repository).get()

        print("[+] pushing git files to upstream")
        print("[+] (please ensure the public key is allowed on remote git repository)")
        self.tools.waitsfor(cn, "cd %s && git push origin master" % repository)

        return True

    def blueprint_configuration(self, cid, csecret, organization, stor_org, stor_ns, stor_cid, stor_secret):
        """
        cid: iyo-client-id to generate a jwt
        csecret: iyo-client-secret to generate a jwt
        organization: organization name
        stor_org: 0-stor organization root name
        stor_ns: 0-stor organization namespace
        stor_cid: 0-stor itsyou.online client id
        stor_secret: 0-stor itsyou.online client secret

        this return the jwt token for ays
        """
        cn = self.node.containers.get(self.ctname)

        print("[+] requesting jwt token for ays")
        token = self.tools.generatetoken(cid, csecret, organization, 3600)

        #
        # configuration.bp
        #
        print("[+] building configuration blueprint")

        source = cn.client.bash("cat %s/configuration.yaml" % self.templates).get()
        config = yaml.load(source.stdout)

        # configuring blueprint
        for item in config['configuration__main']['configurations']:
            if item['key'] == '0-core-version':
                item['value'] = self.core_version

            if item['key'] == 'jwt-token':
                item['value'] = token

            if item['key'] == '0-stor-organization':
                item['value'] = stor_org

            if item['key'] == '0-stor-namespace':
                item['value'] = stor_ns

            if item['key'] == '0-stor-clientid':
                item['value'] = stor_cid

            if item['key'] == '0-stor-clientsecret':
                item['value'] = stor_secret

        blueprint = "/optvar/cockpit_repos/orchestrator-server/blueprints/configuration.bp"
        fd = cn.client.filesystem.open(blueprint, "w")
        cn.client.filesystem.write(fd, yaml.dump(config).encode('utf-8'))
        cn.client.filesystem.close(fd)

        return token

    def blueprint_network(self, network, vlan, cidr):
        """
        network: network type (g8, switchless, packet)
        vlan and cidr: argument for g8 and switchless setup

        Note: network value is not verified, please ensure the network passed
              is a valid value, if value is not correct, the behavior is unexpected (crash)
        """
        cn = self.node.containers.get(self.ctname)

        #
        # network.bp
        #
        print("[+] building network blueprint")
        targets = {
            'g8': 'zero-os',
            'switchless': 'switchless'
        }

        source = cn.client.bash("cat %s/network-%s.yaml" % (self.templates, network)).get()
        netconfig = yaml.load(source.stdout)

        if network in ['g8', 'switchless']:
            key = 'network.%s__storage' % targets[network]

            netconfig[key]['vlanTag'] = int(vlan)
            netconfig[key]['cidr'] = cidr

        if network in ['packet']:
            # there is nothing to do, but we keep the code
            # to know we _explicitly_ does nothing
            pass

        blueprint = "/optvar/cockpit_repos/orchestrator-server/blueprints/network.bp"
        fd = cn.client.filesystem.open(blueprint, "w")
        cn.client.filesystem.write(fd, yaml.dump(netconfig).encode('utf-8'))
        cn.client.filesystem.close(fd)

        return True

    def blueprint_bootstrap(self, znetid, ztoken):
        """
        znetid: zerotier netword id of the nodes
        ztoken: zerotier token to manage nodes network
        """
        cn = self.node.containers.get(self.ctname)

        #
        # bootstrap.bp
        #
        print("[+] building bootstrap blueprint")

        source = cn.client.bash("cat %s/bootstrap.yaml" % self.templates).get()
        bstrapconfig = yaml.load(source.stdout)

        bstrapconfig['bootstrap.zero-os__grid1']['zerotierNetID'] = znetid
        bstrapconfig['bootstrap.zero-os__grid1']['zerotierToken'] = ztoken

        blueprint = "/optvar/cockpit_repos/orchestrator-server/blueprints/bootstrap.bp"
        fd = cn.client.filesystem.open(blueprint, "w")
        cn.client.filesystem.write(fd, yaml.dump(bstrapconfig).encode('utf-8'))
        cn.client.filesystem.close(fd)

        return True

    def starter(self, email, domain=None, organization=None):
        jobs = {}
        cn = self.node.containers.get(self.ctname)

        running = self.running_processes(cn)
        if len(running) == 3:
            print("[+] all processes already running")
            return

        if 'ays' not in running:
            print("[+] starting ays")
            jobs['ays'] = cn.client.system('python3 main.py --host 127.0.0.1 --port 5000 --log info', dir='/opt/code/github/jumpscale/ays9')

        if 'orchestrator' not in running:
            print("[+] starting 0-orchestrator")
            if organization:
                jobs['orchestrator'] = cn.client.system('/usr/local/bin/orchestratorapiserver --bind localhost:8080 --ays-url http://127.0.0.1:5000 --ays-repo orchestrator-server --org "%s"' % organization)

            else:
                jobs['orchestrator'] = cn.client.system('/usr/local/bin/orchestratorapiserver --bind localhost:8080 --ays-url http://127.0.0.1:5000 --ays-repo orchestrator-server')

        if 'caddy' not in running:
            if domain:
                caddyfile = """
                %s {
                    proxy / localhost:8080
                }
                """ % domain
            else:
                caddyfile = """
                :443 {
                    proxy / localhost:8080
                    tls self_signed
                }
                :80 {
                    proxy / localhost:8080
                }
                """

            print("[+] starting caddy")
            cn.client.filesystem.mkdir('/etc/caddy')

            fd = cn.client.filesystem.open("/etc/caddy/Caddyfile", "w")
            cn.client.filesystem.write(fd, caddyfile.encode('utf-8'))
            cn.client.filesystem.close(fd)

            jobs['caddy'] = cn.client.system('/usr/local/bin/caddy -agree -email %s -conf /etc/caddy/Caddyfile -quic' % email)

        print("[+] all processes started")

    def deploy(self, jwt):
        print("[+] deploying blueprints")
        cn = self.node.containers.get(self.ctname)

        repository = "/optvar/cockpit_repos/orchestrator-server"
        blueprints = ["configuration.bp", "network.bp", "bootstrap.bp"]
        environ = {'JWT': jwt}

        print("[+] waiting for ays to boot")

        status = 'ERROR'
        while status != 'SUCCESS':
            reply = cn.client.system("ays repo list", env=environ).get()
            status = reply.state

        print("[+] ays ready, executing blueprints")

        for blueprint in blueprints:
            print("[+] executing: %s" % blueprint)
            x = cn.client.system("ays blueprint %s" % blueprint, dir=repository, env=environ).get()

        return True

    def running_processes(self, cn):
        running = set()

        for ps in cn.client.process.list():
            if ps['cmdline'].find("caddy") != -1:
                running.add('caddy')

            if ps['cmdline'].find("orchestratorapiserver") != -1:
                running.add('orchestrator')

            if ps['cmdline'].find("/opt/jumpscale9/bin/python3 main.py") != -1:
                running.add('ays')

        return running

    """
    You can just extends this class to implements theses hooks
    This will allows you to customize the setup
    """
    def pre_prepare(self):
        pass

    def post_prepare(self):
        pass

    def pre_configure(self):
        pass

    def post_configure(self):
        pass

    def pre_starter(self):
        pass

    def post_starter(self):
        pass


if __name__ == "__main__":
    print("[+] initializing orchestrator bootstrapper")
    installer = OrchestratorInstaller()
    warning = False

    parser = argparse.ArgumentParser(description='Manage Threefold Orchestrator')
    parser.add_argument('--server', type=str, help='zero-os remote server to connect', required=True)
    parser.add_argument('--password', type=str, help='password (jwt) used to connect the host')
    parser.add_argument('--flist', type=str, help='flist container base image')
    parser.add_argument('--container', type=str, help='container deployment name', required=True)
    parser.add_argument('--domain', type=str, help='domain on which caddy should be listening, if not specified caddy will listen on port 80 and 443, but with self-signed certificate')
    parser.add_argument('--zt-net', type=str, help='zerotier network id of the container', required=True)
    parser.add_argument('--upstream', type=str, help='remote upstream git address', required=True)
    parser.add_argument('--email', type=str, help='email used by caddy for certificates')
    parser.add_argument('--organization', type=str, help='itsyou.online organization of ays')
    parser.add_argument('--client-id', type=str, help='itsyou.online client-id for jwt-token', required=True)
    parser.add_argument('--client-secret', type=str, help='itsyou.online client-secret for jwt-token', required=True)
    parser.add_argument('--ssh-key', type=str, help='ssh private key filename (need to be passphrase less')
    parser.add_argument('--network', type=str, help='network type: g8, switchless, packet', required=True)
    parser.add_argument('--network-vlan', type=str, help='g8/switchless only: vlan id')
    parser.add_argument('--network-cidr', type=str, help='g8/switchless only: cidr address')
    parser.add_argument('--nodes-zt-net', type=str, help='zerotier network id of the nodes', required=True)
    parser.add_argument('--nodes-zt-token', type=str, help='zerotier token to manage the nodes', required=True)
    parser.add_argument('--stor-organization', type=str, help='0-stor organization name as root (default: --organization)')
    parser.add_argument('--stor-namespace', type=str, help='0-stor root namespace to use (default: namespace)')
    parser.add_argument('--stor-client-id', type=str, help='0-stor itsyou.online client id (default: --client-id)')
    parser.add_argument('--stor-client-secret', type=str, help='0-stor itsyou.online client secret (default: --client-secret)')
    args = parser.parse_args()

    if args.email == None:
        args.email = "info@gig.tech"

    if args.flist:
        installer.flist = args.flist

    if args.network not in ['g8', 'switchless', 'packet']:
        print("[-] error: network: invalid network type '%s'" % args.network)
        sys.exit(1)

    if args.network in ['g8', 'switchless']:
        if not args.network_vlan or not args.network_cidr:
            print("[-] error: network %s: vlan and cird required" % args.network)
            sys.exit(1)

    if not args.stor_organization or not args.stor_namespace or not args.stor_client_id or not args.stor_client_secret:
        print("[-] warning: 0-stor: values not fully explicitly specified")
        print("[-] warning: 0-stor: some of them will be set implicitly")

    if installer.tools.ssh.localkeys() == "" and not args.ssh_key:
        print("[-] error: ssh-agent: no keys found on ssh-agent and")
        print("[-] error: ssh-agent: no ssh private key specified")
        print("[-] error: ssh-agent: you need at least one of them")
        sys.exit(1)

    sshkey = None
    if args.ssh_key:
        sshkey = installer.tools.ssh.loadkey(args.ssh_key)

        if not installer.tools.ssh.validkey(sshkey):
            print("[-] error: ssh-key: invalid ssh key file")
            sys.exit(1)

        if installer.tools.ssh.encryptedkey(sshkey):
            print("[-] error: ssh-key: private key encrypted")
            print("[-] error: ssh-key: you need to provided a passphrase-less key")
            sys.exit(1)

    stor_organization = args.stor_organization if args.stor_organization else args.organization
    stor_namespace = args.stor_namespace if args.stor_namespace else "namespace"
    stor_clientid = args.stor_client_id if args.stor_client_id else args.client_id
    stor_clientsecret = args.stor_client_secret if args.stor_client_secret else args.client_secret

    print("[+] ===============================================================")
    print("[+] -- global -----------------------------------------------------")
    print("[+] remote server   : %s" % args.server)
    print("[+] root zt network : %s" % args.zt_net)
    print("[+] nodes zt network: %s" % args.nodes_zt_net)
    print("[+] container flist : %s" % installer.flist)
    print("[+] container name  : %s" % args.container)
    print("[+] ssh private key : %s" % args.ssh_key)
    print("[+] domain name     : %s" % args.domain)
    print("[+] upstream git    : %s" % args.upstream)
    print("[+] global email    : %s" % args.email)
    print("[+] ays organization: %s" % args.organization)
    print("[+]")
    print("[+] -- 0-stor -----------------------------------------------------")
    print("[+] organization    : %s" % stor_organization)
    print("[+] namespace       : %s" % stor_namespace)
    print("[+] client id       : %s" % stor_clientid)
    print("[+]")
    print("[+] -- network ----------------------------------------------------")
    print("[+] network type    : %s" % args.network)
    print("[+] optional vlan id: %s" % args.network_vlan)
    print("[+] optional range  : %s" % args.network_cidr)
    print("[+] ===============================================================")
    print("[+]")

    print("[+] initializing connection")
    node = installer.connector(args.server, args.password)

    print("[+] hook: pre-prepare")
    installer.pre_prepare()

    print("[+] hook: prepare")
    prepared = installer.prepare(args.container, args.zt_net, args.nodes_zt_net, sshkey)

    print("[+] ==================================================")
    print("[+] container address: %s" % prepared['address'])
    print("[+] container key: %s" % prepared['publickey'])
    print("[+] ==================================================")

    print("[+] hook: post-prepare")
    installer.post_prepare()

    print("[+] hook: pre-configure")
    installer.pre_configure()

    print("[+] hook: configure")
    installer.configure(args.upstream, args.email, args.organization)

    token = installer.blueprint_configuration(
        args.client_id, args.client_secret, args.organization,
        stor_organization, stor_namespace, stor_clientid, stor_clientsecret
    )

    installer.blueprint_network(args.network, args.network_vlan, args.network_cidr)
    installer.blueprint_bootstrap(args.nodes_zt_net, args.nodes_zt_token)

    print("[+] hook: post-configure")
    installer.post_configure()

    print("[+] hook: pre-starter")
    installer.pre_starter()

    print("[+] hook: starter")
    installer.starter(args.email, args.domain, args.organization)
    installer.deploy(token)

    print("[+] hook: post-starter")
    installer.post_starter()
