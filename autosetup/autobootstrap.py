#!/usr/bin/python3
import argparse
import subprocess
import requests
import sys
import time
import yaml
import pytoml as toml
from jose import jwt
from urllib.parse import urlparse
from zeroos.orchestrator.sal.Node import Node
from zerotier import client as ztclient

class ZerotierAuthorizer:
    def __init__(self, token):
        self.client = ztclient.Client()
        self.client.set_auth_header("Bearer " + token)

    def validate(self, networkid):
        try:
            x = self.client.network.getNetwork(networkid)
            return True

        except Exception:
            return False

    def memberMacAddress(self, memberid, networkid):
        """
        This code is a python-port of the code used in the web-ui interface
        Found on the web-ui javascript code, it compute the client mac-address
          based on client id and network id
        """
        n = int(networkid[0:8] or "0", 16)
        r = int(networkid[8:16] or "0", 16)
        i = 254 & r | 2

        if i == 82:
            i = 50

        o = i << 8 & 65280
        while True:
            o |= 255 & (int(memberid[0:2], 16) or 0)
            o ^= r >> 8 & 255
            if len("%04x" % o) == 4:
                break

        a = int(memberid[2:6], 16)
        while True:
            a ^= (r >> 16 & 255) << 8
            a ^= r >> 24 & 255
            if len("%04x" % a) == 4:
                break

        s = int(memberid[6:10], 16)
        while True:
            s ^= (255 & n) << 8
            s ^= n >> 8 & 255
            if len("%04x" % s) == 4:
                break

        def segment(source):
            computed = "%04x" % source
            return "%s:%s" % (computed[0:2], computed[2:4])

        return "%s:%s:%s" % (segment(o), segment(a), segment(s))

    def authorize_node(self, member):
        member['config']['authorized'] = True
        self.client.network.updateMember(member, member['nodeId'], member['networkId'])

    def memberFromMac(self, networkid, hwaddr):
        members = self.client.network.listMembers(networkid).json()

        for member in members:
            usermac = self.memberMacAddress(member['nodeId'], networkid)
            if usermac == hwaddr:
                return member

        return None

    def authorize(self, networkid, hwaddr):
        netinfo = self.client.network.getNetwork(networkid).json()
        netname = netinfo['config']['name']

        member = self.memberFromMac(networkid, hwaddr)
        if not member:
            print("[-] member not found, you should waits for it before")
            return None

        self.authorize_node(member)

class OrchestratorJWT:
    def __init__(self, token):
        self.jwt = token
        self.data = jwt.get_unverified_claims(token)

    def organization(self):
        for scope in self.data['scope']:
            if scope.startswith('user:memberof:'):
                return scope.split(':')[2]

        return None

    def isValid(self):
        try:
            jwt._validate_exp(self.jwt)
            return True

        except Exception:
            return False

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
        while True:
            self.progressing()

            # get and ensure mac address is there
            status = self.ztstatus(cn, macaddr)
            if not status:
                return None

            for addr in status['assignedAddresses']:
                # checking for ipv4, rejecting ipv6
                if "." in addr:
                    # network ready, address set
                    self.progressing(True)
                    return addr.split('/')[0]

            time.sleep(1)
            continue

    def ztdiscover(self, authorizer, networkid, hwaddr):
        while True:
            self.progressing()

            if authorizer.memberFromMac(networkid, hwaddr):
                self.progressing(final=False, step=True)
                return True

            time.sleep(1)

    def containerzt(self, cn, authorizer, nwid=None):
        # for all zerotier network, waiting for a valid address
        ztinfo = cn.client.zerotier.list()

        for ztnet in ztinfo:
            # only process specific nwid if provided
            if nwid and ztnet['nwid'] != nwid:
                continue

            print("[+] waiting zerotier access (id: %s, hardware: %s)" % (ztnet['nwid'], ztnet['mac']))
            self.progress()

            # waiting for client discovered
            self.ztdiscover(authorizer, ztnet['nwid'], ztnet['mac'])

            # self-authorizing client
            authorizer.authorize(ztnet['nwid'], ztnet['mac'])

            # waiting for ip-address
            return self.ztwait(cn, ztnet['mac'])


    def progress(self):
        self.xprint("[+] ")

    def progressing(self, final=False, step=False):
        progression = "." if not step else "+"
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

    def prepare(self, ctname, ztnet, ztnetnodes, sshkey, ztauthnodes, ztauth):
        """
        node: connected node object
        ctname: container name
        ztnetwork: zerotier network the container should join
        """
        self.ctname = ctname

        print("[+] starting orchestrator container")
        network = [
            {'type': 'default'},
            {'type': 'zerotier', 'id': ztnet}
        ]

        if ztnetnodes != ztnet:
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

        #
        # waiting for zerotier
        #
        containeraddrs = []

        print("[+] configuring zerotier-nodes access")
        containeraddrs.append(self.tools.containerzt(cn, ztauthnodes, ztnetnodes))

        if ztauth:
            print("[+] configuring zerotier-orchestrator access")
            containeraddrs.append(self.tools.containerzt(cn, ztauth, ztnet))

        #
        # install or generate ssh key
        #
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

        return {'address': containeraddrs, 'publickey': publickey.stdout.strip()}

    def configure(self, upstream, email, organization):
        """
        upstream: git upstream address of orchestrator repository
        email: email address used for git and caddy certificates
        organization: organization name ays should allows
        """
        print("[+] configuring services")
        cn = self.node.containers.get(self.ctname)

        #
        # configuring ays
        #
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

        #
        # setting up git
        #
        print("[+] configuring git client")
        cn.client.bash("git config --global user.name 'AYS System'").get()
        cn.client.bash("git config --global user.email '%s'" % email).get()

        #
        # setting up upstream
        #
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

    def blueprint_configuration(self, cluster_token):
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
                item['value'] = cluster_token

        blueprint = "/optvar/cockpit_repos/orchestrator-server/blueprints/configuration.bp"
        fd = cn.client.filesystem.open(blueprint, "w")
        cn.client.filesystem.write(fd, yaml.dump(config).encode('utf-8'))
        cn.client.filesystem.close(fd)

        return True

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

    def starter(self, email, organization, orchjwt):
        jobs = {}
        cn = self.node.containers.get(self.ctname)

        running = self.running_processes(cn)
        if len(running) == 3:
            print("[+] all processes already running")
            return

        if 'ays' not in running:
            print("[+] starting ays")
            arguments = [
                'python3',
                'main.py',
                '--host 127.0.0.1',
                '--port 5000',
                '--log info'
            ]
            jobs['ays'] = cn.client.system(" ".join(arguments), dir='/opt/code/github/jumpscale/ays9')

        if 'orchestrator' not in running:
            print("[+] starting 0-orchestrator")
            arguments = [
                '/usr/local/bin/orchestratorapiserver',
                '--bind localhost:8080',
                '--ays-url http://127.0.0.1:5000',
                '--ays-repo orchestrator-server',
                '--org "%s"' % organization,
                '--jwt "%s"' % orchjwt
            ]

        if 'caddy' not in running:
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

            arguments = [
                '/usr/local/bin/caddy',
                '-agree',
                '-email %s' % email,
                '-conf /etc/caddy/Caddyfile',
                '-quic'
            ]
            jobs['caddy'] = cn.client.system(" ".join(arguments))

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

    def validate(self, ztauthorizer, zt_network):
        if not ztauthorizer.validate(zt_network):
            print("[-] error: cannot validate zerotier network %s" % zt_network)
            print("[-] error: incorrect token provided, abording")
            sys.exit(1)

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
    print("[+] ================================")
    print("[+] == Zero-OS Orchestrator Setup ==")
    print("[+] ================================")
    print("[+]")
    installer = OrchestratorInstaller()

    parser = argparse.ArgumentParser(description='Zero-OS Orchestrator Setup')

    parser.add_argument('--host',     type=str, help='remote Zero-OS server (address or hostname)', required=True)
    parser.add_argument('--host-jwt', type=str, help='(optional) iyo jwt to use to connect the host')

    parser.add_argument('--host-iyo-organization',  type=str, help='(optional) iyo organization to generate host-jwt')
    parser.add_argument('--host-iyo-client-id',     type=str, help='(optional) iyo client-id to generate host-jwt')
    parser.add_argument('--host-iyo-client-secret', type=str, help='(optional) iyo client-secret to generate host-jwt')

    parser.add_argument('--orchestrator-container-flist',  type=str, help='containers flist base image')
    parser.add_argument('--orchestrator-container-name',   type=str, help='container deployment name', default="orchestrator")
    parser.add_argument('--orchestrator-iyo-organization', type=str, help='itsyou.online organization of ays', required=True)

    parser.add_argument('--orchestrator-zt-net',      type=str, help='zerotier network id of the container', required=True)
    parser.add_argument('--orchestrator-zt-token',    type=str, help='(optional) zerotier api token to auto-authorize orchestrator')
    parser.add_argument('--orchestrator-git-repo',    type=str, help='remote upstream git address', required=True)
    parser.add_argument('--orchestrator-git-email',   type=str, help='email used by caddy for certificates (default: info@gig.tech)', default="info@gig.tech")
    parser.add_argument('--orchestrator-git-ssh-key', type=str, help='ssh private key filename (need to be passphrase less)')

    parser.add_argument('--cluster-jwt', type=str, help='refreshable jwt token with (for orchestrator api)')

    parser.add_argument('--cluster-iyo-organization',     type=str, help='itsyou.online organization for cluster-jwt generator')
    parser.add_argument('--cluster-iyo-client-id',        type=str, help='itsyou.online client-id for cluster-jwt generator')
    parser.add_argument('--cluster-iyo-client-secret',    type=str, help='itsyou.online client-secret for cluster-jwt generator')
    parser.add_argument('--cluster-backend-network-type', type=str, help='network type: g8, switchless, packet', required=True)
    parser.add_argument('--cluster-backend-network-vlan', type=str, help='g8/switchless only: vlan id')
    parser.add_argument('--cluster-backend-network-cidr', type=str, help='g8/switchless only: cidr address')
    parser.add_argument('--cluster-management-zt-net',    type=str, help='zerotier-network id of the cluster-nodes', required=True)
    parser.add_argument('--cluster-management-zt-token',  type=str, help='zerotier-token to manage the cluster-nodes', required=True)

    parser.add_argument('--dry-run', help='only shows arguments summary, tokens and tests status (no install)', action="store_true")
    args = parser.parse_args()

    #
    # obvious and fast argument checking
    #
    print("[+] preliminary arguments verification")

    if args.orchestrator_container_flist:
        installer.flist = args.orchestrator_container_flist

    # checking host authentification method provided
    host_auth_method = "jwt" if args.host_jwt else "iyo"
    if host_auth_method == "iyo":
        # jwt is not set, let's check if no iyo is set
        if not args.host_iyo_organization and not args.host_iyo_client_id and not args.host_iyo_client_secret:
            # no iyo set and no jwt token set
            # we assume there is no password protection on host
            host_auth_method = "unprotected"

        else:
            # some iyo argument was given, let's check if he wave all of them
            if not args.host_iyo_organization or not args.host_iyo_client_id or not args.host_iyo_client_secret:
                print("[-] error: auth: no --host-jwt provided and incomplete --host-iyo-xxx arguments")
                print("[-] error: auth: please provide a jwt or all iyo arguments")
                sys.exit(1)

    # checking cluster authentification method provided
    cluster_auth_method = "jwt" if args.cluster_jwt else "iyo"
    if cluster_auth_method == "iyo":
        # we don't have jwt for cluster so we need to generate it
        # checking if we have all required argument for that
        if not args.cluster_iyo_organization or not args.cluster_iyo_client_id or not args.cluster_iyo_client_secret:
            print("[-] error: auth: no --cluster-jwt provided and incomplete --cluster-iyo-xxx arguments")
            print("[-] error: auth: please provide a jwt or all iyo arguments")
            sys.exit(1)

    # checking cluster backend network validity
    if args.cluster_backend_network_type not in ['g8', 'switchless', 'packet']:
        print("[-] error: network: invalid network type '%s'" % args.cluster_backend_network_type)
        sys.exit(1)

    if args.cluster_backend_network_type in ['g8', 'switchless']:
        if not args.cluster_backend_network_vlan or not args.cluster_backend_network_cidr:
            print("[-] error: network %s: vlan and cird required" % args.cluster_backend_network_type)
            sys.exit(1)

    # checking upstream ssh key validity if provided
    if installer.tools.ssh.localkeys() == "" and not args.orchestrator_git_ssh_key:
        print("[-] error: ssh-agent: no keys found on ssh-agent and no ssh private key specified")
        print("[-] error: ssh-agent: you need at least one of them")
        sys.exit(1)

    sshkey = None
    if args.orchestrator_git_ssh_key:
        sshkey = installer.tools.ssh.loadkey(args.orchestrator_git_ssh_key)

        if not installer.tools.ssh.validkey(sshkey):
            print("[-] error: ssh-key: invalid ssh key file")
            sys.exit(1)

        if installer.tools.ssh.encryptedkey(sshkey):
            print("[-] error: ssh-key: private key encrypted")
            print("[-] error: ssh-key: you need to provided a passphrase-less key")
            sys.exit(1)

    #
    # arguments syntax looks okay, let's show a small summary
    #
    print("[+]")
    print("[+] -- global -----------------------------------------------------")
    print("[+] remote server        : %s" % args.host)
    print("[+] authentification     : %s" % host_auth_method)
    print("[+] iyo organization     : %s" % args.host_iyo_organization)
    print("[+] iyo client-id        : %s" % args.host_iyo_client_id)
    print("[+] iyo client-secret    : %s" % ("[ok-hidden]" if args.host_iyo_client_secret else "None"))
    print("[+]")
    print("[+] -- zerotier ---------------------------------------------------")
    print("[+] orchestrator network : %s" % args.orchestrator_zt_net)
    print("[+] orchestrator token   : %s" % ("[ok-hidden]" if args.orchestrator_zt_token else "None"))
    print("[+] cluster nodes network: %s" % args.cluster_management_zt_net)
    print("[+] cluster nodes token  : %s" % ("[ok-hidden]" if args.cluster_management_zt_token else "None"))
    print("[+]")
    print("[+] -- orchestrator -----------------------------------------------")
    print("[+] container flist url  : %s" % installer.flist)
    print("[+] container name       : %s" % args.orchestrator_container_name)
    print("[+] iyo organization     : %s" % args.orchestrator_iyo_organization)
    print("[+]")
    print("[+] -- upstream ---------------------------------------------------")
    print("[+] ssh private key      : %s" % args.orchestrator_git_ssh_key)
    print("[+] upstream git email   : %s" % args.orchestrator_git_email)
    print("[+] upstream repository  : %s" % args.orchestrator_git_repo)
    print("[+]")
    print("[+] -- cluster ----------------------------------------------------")
    print("[+] refreshable jwt      : %s" % args.cluster_jwt)
    print("[+] iyo organization     : %s" % args.cluster_iyo_organization)
    print("[+] iyo client-id (jwt)  : %s" % args.cluster_iyo_client_id)
    print("[+] iyo client-secret    : %s" % ("[ok-hidden]" if args.cluster_iyo_client_secret else "None"))
    print("[+]")
    print("[+] -- network ----------------------------------------------------")
    print("[+] backend network set : %s" % args.cluster_backend_network_type)
    print("[+] backend vlan-id     : %s" % args.cluster_backend_network_vlan)
    print("[+] backend address cidr: %s" % args.cluster_backend_network_cidr)
    print("[+]")
    print("[+] ===============================================================")
    print("[+]")

    # print("[+] -- notice -----------------------------------------------------")
    # print("[-] take some time to review summary")
    # print("[+] setup will continue in 5 seconds, press CTRL+C now to cancel")
    # time.sleep(5)

    #
    # now let's validate argument we can validate now
    # this will reduce risk of unexpected behavior during deployment
    # caused by some incorrect token, credentials or so...
    #
    print("[+] preliminary checks")

    #
    # testing zerotier tokens
    #
    print("[+] checking zerotier token for network: %s" % args.cluster_management_zt_net)
    zt_auth_cluster = ZerotierAuthorizer(args.cluster_management_zt_token)
    installer.validate(zt_auth_cluster, args.cluster_management_zt_net)

    zt_auth_container = None
    if args.orchestrator_zt_token:
        print("[+] checking zerotier token for network: %s" % args.orchestrator_zt_net)
        zt_auth_container = ZerotierAuthorizer(args.orchestrator_zt_token)
        installer.validate(zt_auth_container, args.orchestrator_zt_net)

    #
    # generating jwt tokens if not provided
    #
    if host_auth_method == "iyo":
        print("[+] generating host-jwt based on iyo-arguments")
        args.host_jwt = installer.tools.generatetoken(
            args.host_iyo_client_id,
            args.host_iyo_client_secret,
            args.host_iyo_organization,
            3600
        )

    if cluster_auth_method == "iyo":
        print("[+] generating cluster-jwt based on iyo-arguments")
        args.cluster_jwt = installer.tools.generatetoken(
            args.cluster_iyo_client_id,
            args.cluster_iyo_client_secret,
            args.cluster_iyo_organization,
            3600
        )

    #
    # checking validity of the tokens (even if we generated them)
    # a jwt can be granted but not contains organization requested
    # if the user is not member of the organization, we check now so
    # we can avoid error later
    #
    if args.host_jwt:
        print("[+] parsing provided (or generated) host-jwt")

        host_jwt = OrchestratorJWT(args.host_jwt)
        # did we generated it ourself
        if args.host_iyo_organization:
            # does the user is part of the organization
            if host_jwt.organization() != args.host_iyo_organization:
                print("[-] error: host-jwt: user is not part of the organization: %s" % args.host_iyo_organization)
                sys.exit(1)

        if not host_jwt.isValid():
            print("[-] error: host-jwt: token is expired")
            sys.exit(1)

    print("[+] parsing provided (or generated) cluster-jwt")
    cluster_jwt = OrchestratorJWT(args.cluster_jwt)

    if cluster_auth_method == "jwt":
        # user provided a jwt, extracting organization from it
        args.cluster_iyo_organization = cluster_jwt.organization()
        # we know that next step will always be true, but let's keep
        # the code generic

    if cluster_jwt.organization() != args.cluster_iyo_organization:
        print("[-] error: cluster-jwt: user is not part of the organization: %s" % args.cluster_iyo_organization)
        sys.exit(1)

    if not cluster_jwt.isValid():
        print("[-] error: host-jwt: token is expired")
        sys.exit(1)

    print("[+]")
    print("[+] -- jwt tokens -------------------------------------------------")
    if args.host_jwt:
        print("[+] host jwt organization: %s" % host_jwt.organization())

    print("[+] cluster jwt organization: %s" % cluster_jwt.organization())
    print("[+]")

    print("[+] == wouhou ==")

    if args.dry_run:
        print("[+] everything looks correct, you asked a dry-run, nothing more do do")
        sys.exit(0)

    print("[+] everything looks correct, let's go installing all of this !")
    print("[+]")

    #
    # everything looks fine for now
    # starting the real deployment
    #
    print("[+] initializing connection")
    node = installer.connector(args.host, args.host_jwt)

    print("[+] hook: pre-prepare")
    installer.pre_prepare()

    print("[+] hook: prepare")
    prepared = installer.prepare(
        args.orchestrator_container_name,
        args.orchestrator_zt_net,
        args.cluster_management_zt_net,
        sshkey,
        zt_auth_cluster,
        zt_auth_container
    )

    print("[+] ==================================================")
    print("[+] container address: %s" % prepared['address'])
    print("[+] container key: %s" % prepared['publickey'])
    print("[+] ==================================================")

    print("[+] hook: post-prepare")
    installer.post_prepare()

    print("[+] hook: pre-configure")
    installer.pre_configure()

    print("[+] hook: configure")
    installer.configure(
        args.orchestrator_git_repo,
        args.orchestrator_git_email,
        args.cluster_iyo_organization
    )

    installer.blueprint_configuration(args.cluster_jwt)
    installer.blueprint_network(
        args.cluster_backend_network_type,
        args.cluster_backend_network_vlan,
        args.cluster_backend_network_cidr
    )
    installer.blueprint_bootstrap(
        args.cluster_management_zt_net,
        args.cluster_management_zt_token
    )

    print("[+] hook: post-configure")
    installer.post_configure()

    print("[+] hook: pre-starter")
    installer.pre_starter()

    print("[+] hook: starter")
    installer.starter(
        args.orchestrator_git_email,
        args.orchestrator_iyo_organization,
        args.cluster_jwt
    )
    installer.deploy(args.cluster_jwt)

    print("[+] hook: post-starter")
    installer.post_starter()

    print("[+] orchestrator deployed, have a nice day")
