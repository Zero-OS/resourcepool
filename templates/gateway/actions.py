from js9 import j


def input(job):
    import ipaddress

    domain = job.model.args.get('domain')
    if not domain:
        raise j.exceptions.Input('Domain cannot be empty.')

    nics = job.model.args.get('nics', [])
    for nic in nics:
        config = nic.get('config', {})
        name = nic.get('name')
        if not name:
            raise j.exceptions.Input("NIC should has a name".format(name=name))
        if name[0].isnumeric():
            raise j.exceptions.Input("Bad nic definition '{name}', name shouldn't start with a number".format(name=name))
        dhcp = nic.get('dhcpserver')
        zerotierbridge = nic.get('zerotierbridge')
        cidr = config.get('cidr')

        if zerotierbridge and not zerotierbridge.get('id'):
            raise j.exceptions.Input('Zerotierbridge id not specified')

        if not name:
            raise j.exceptions.Input('Gateway nic should have name defined.')

        if config:
            if config.get('gateway'):
                if dhcp:
                    raise j.exceptions.Input('DHCP can only be defined for private networks')

        if dhcp:
            if not cidr:
                raise j.exceptions.Input('Gateway nic should have cidr if a DHCP server is defined.')
            nameservers = dhcp.get('nameservers')

            if not nameservers:
                raise j.exceptions.Input('DHCP nameservers should have at least one nameserver.')
            hosts = dhcp.get('hosts', [])
            subnet = ipaddress.IPv4Interface(cidr).network
            for host in hosts:
                ip = host.get('ipaddress')
                if not ip or not ipaddress.ip_address(ip) in subnet:
                    raise j.exceptions.Input('Dhcp host ipaddress should be within cidr subnet.')

    return job.model.args


def init(job):
    from zeroos.orchestrator.configuration import get_configuration

    service = job.service
    containeractor = service.aysrepo.actorGet("container")
    nics = service.model.data.to_dict()['nics']  # get dict version of nics
    for nic in nics:
        nic.pop('dhcpserver', None)
        zerotierbridge = nic.pop('zerotierbridge', None)
        if zerotierbridge:
            nics.append(
                {
                    'id': zerotierbridge['id'], 'type': 'zerotier',
                    'name': 'z-{}'.format(nic['name']), 'token': zerotierbridge.get('token', '')
                })

    config = get_configuration(service.aysrepo)

    args = {
        'node': service.model.data.node,
        'flist': config.get('gw-flist', 'https://hub.gig.tech/gig-official-apps/zero-os-gw-master.flist'),
        'nics': nics,
        'hostname': service.model.data.hostname,
        'hostNetworking': False,
        "privileged": True
    }
    cont_service = containeractor.serviceCreate(instance=service.name, args=args)
    service.consume(cont_service)

    args = {
        'container': service.name
    }

    # create firewall
    fwactor = service.aysrepo.actorGet('firewall')
    fwactor.serviceCreate(instance=service.name, args=args)

    # create http
    httpactor = service.aysrepo.actorGet('http')
    httpactor.serviceCreate(instance=service.name, args=args)

    # create dhcp
    dhcpactor = service.aysrepo.actorGet('dhcp')
    dhcpactor.serviceCreate(instance=service.name, args=args)

    # Start cloudinit
    cloudinitactor = service.aysrepo.actorGet("cloudinit")
    cloudinitactor.serviceCreate(instance=service.name, args=args)


def install(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('start', context=job.context))

def save_certificates(job, container, caddy_dir="/.caddy"):
    from io import  BytesIO
    if container.client.filesystem.exists(caddy_dir):
        service = job.service
        certificates = []
        for cert_authority in container.client.filesystem.list("{}/acme/".format(caddy_dir)):
            if cert_authority['is_dir']:
                users = []
                sites = []
                if container.client.filesystem.exists("{}/acme/{}/users".format(caddy_dir, cert_authority['name'])):
                    users = container.client.filesystem.list("{}/acme/{}/users".format(caddy_dir, cert_authority['name']))
                if container.client.filesystem.exists("{}/acme/{}/sites".format(caddy_dir, cert_authority['name'])):
                    sites = container.client.filesystem.list("{}/acme/{}/sites".format(caddy_dir, cert_authority['name']))
                for user in users:
                    if user['is_dir']:
                        cert_path = "{}/acme/{}/users/{}".format(caddy_dir, cert_authority['name'], user['name'])

                        metadata_buf = BytesIO()
                        if container.client.filesystem.exists("{}/{}.json".format(cert_path, user['name'])):
                            container.client.filesystem.download("{}/{}.json".format(cert_path, user['name']), metadata_buf)
                        else:
                            continue

                        key_buf = BytesIO()
                        if container.client.filesystem.exists("{}/{}.key".format(cert_path, user['name'])):
                            container.client.filesystem.download("{}/{}.key".format(cert_path, user['name']), key_buf)
                        else:
                            continue

                        certificates.append({"path": cert_path, "key": key_buf.getvalue().decode(), "metadata": metadata_buf.getvalue().decode()})

                for site in sites:
                    if site['is_dir']:
                        cert_path = "{}/acme/{}/sites/{}".format(caddy_dir, cert_authority['name'], site['name'])

                        metadata_buf = BytesIO()
                        if container.client.filesystem.exists("{}/{}.json".format(cert_path, site['name'])):
                            container.client.filesystem.download("{}/{}.json".format(cert_path, site['name']), metadata_buf)
                        else:
                            continue

                        key_buf = BytesIO()
                        if container.client.filesystem.exists("{}/{}.key".format(cert_path, site['name'])):
                            container.client.filesystem.download("{}/{}.key".format(cert_path, site['name']), key_buf)
                        else:
                            continue

                        cert_buf = BytesIO()
                        if container.client.filesystem.exists("{}/{}.crt".format(cert_path, site['name'])):
                            container.client.filesystem.download("{}/{}.crt".format(cert_path, site['name']), cert_buf)
                        else:
                            continue

                        certificates.append({
                                        "path": cert_path,
                                        "key": key_buf.getvalue().decode(),
                                        "metadata": metadata_buf.getvalue().decode(),
                                        "cert": cert_buf.getvalue().decode()
                                        })

        service.model.data.certificates = certificates

def restore_certificates(job, container):
    from io import  BytesIO
    service = job.service
    certs = service.model.data.to_dict().get('certificates', [])

    for cert in certs:
        container.client.filesystem.mkdir(cert['path'])
        metadata_buf = BytesIO(cert['metadata'].encode())

        metadata_buf.seek(0)
        container.client.filesystem.upload("{}/{}.json".format(cert['path'], cert['path'].split('/')[-1]), metadata_buf)

        key_buf = BytesIO(cert['key'].encode())
        key_buf.seek(0)
        container.client.filesystem.upload("{}/{}.key".format(cert['path'], cert['path'].split("/")[-1]), key_buf)

        if cert.get('cert'):
            cert_buf = BytesIO(cert['cert'].encode())
            cert_buf.seek(0)
            container.client.filesystem.upload("{}/{}.crt".format(cert['path'], cert['path'].split("/")[-1]), cert_buf)


def get_zerotier_nic(zerotierid, containerobj):
    for zt in containerobj.client.zerotier.list():
        if zt['id'] == zerotierid:
            return zt['portDeviceName']
    else:
        raise j.exceptions.RuntimeError("Failed to get zerotier network device")


def processChange(job):
    from zeroos.orchestrator.configuration import get_jwt_token_from_job
    from zeroos.orchestrator.sal.Container import Container
    service = job.service
    args = job.model.args
    category = args.pop('changeCategory')

    if category != 'dataschema':
        return

    gatewaydata = service.model.data.to_dict()
    nicchanges = gatewaydata['nics'] != args.get('nics')
    httproxychanges = gatewaydata['httpproxies'] != args.get('httpproxies')
    portforwardchanges = gatewaydata['portforwards'] != args.get('portforwards')

    container = service.producers.get('container')[0]
    containerobj = Container.from_ays(container, job.context['token'])

    if nicchanges:
        nics_args = {'nics': args['nics']}

        cloudInitServ = service.aysrepo.serviceGet(role='cloudinit', instance=service.name)
        j.tools.async.wrappers.sync(cloudInitServ.executeAction('update', context=job.context, args=nics_args))

        dhcpServ = service.aysrepo.serviceGet(role='dhcp', instance=service.name)
        j.tools.async.wrappers.sync(dhcpServ.executeAction('update', context=job.context, args=args))

        ip = containerobj.client.ip

        # remove zerotierbridges in old nics
        for nic in service.model.data.to_dict()['nics']:
            zerotierbridge = nic.pop('zerotierbridge', None)
            if zerotierbridge:
                nicname = nic['name']
                linkname = 'l-{}'.format(nicname)[:15]
                zerotiername = get_zerotier_nic(zerotierbridge['id'], containerobj)

                # bring related interfaces down
                ip.link.down(nicname)
                ip.link.down(linkname)
                ip.link.down(zerotiername)

                # remove IPs
                ipaddresses = ip.addr.list(nicname)
                for ipaddress in ipaddresses:
                    ip.addr.delete(nicname, ipaddress)

                # delete interfaces/bridge
                ip.bridge.delif(nicname, zerotiername)
                ip.bridge.delif(nicname, linkname)
                ip.bridge.delete(nicname)

                # rename interface and readd IPs
                ip.link.name(linkname, nicname)
                for ipaddress in ipaddresses:
                    ip.addr.add(nicname, ipaddress)

                # bring interfaces up
                ip.link.up(nicname)
                ip.link.up(zerotiername)

        service.model.data.nics = args['nics']

        # process new nics
        for nic in args['nics']:
            nic.pop('dhcpserver', None)
            zerotierbridge = nic.pop('zerotierbridge', None)
            if zerotierbridge:
                args['nics'].append(
                    {
                        'id': zerotierbridge['id'], 'type': 'zerotier',
                        'name': 'z-{}'.format(nic['name']), 'token': zerotierbridge.get('token', '')
                    })

        # apply changes in container
        cont_service = service.aysrepo.serviceGet(role='container', instance=service.name)
        j.tools.async.wrappers.sync(cont_service.executeAction('processChange', context=job.context, args=nics_args))

        # setup new zerotierbridges
        setup_zerotierbridges(job)

    if nicchanges or portforwardchanges:
        firewallServ = service.aysrepo.serviceGet(role='firewall', instance=service.name)
        j.tools.async.wrappers.sync(firewallServ.executeAction('update', context=job.context, args=args))

    if portforwardchanges:
        service.model.data.portforwards = args.get('portforwards', [])

    if httproxychanges:
        httpproxies = args.get('httpproxies', [])
        httpServ = service.aysrepo.serviceGet(role='http', instance=service.name)
        http_args = {'httpproxies': httpproxies}
        job.context['token'] = get_jwt_token_from_job(job)
        j.tools.async.wrappers.sync(httpServ.executeAction('update', context=job.context, args=http_args))
        service.model.data.httpproxies = httpproxies

    if args.get("domain", None):
        service.model.data.domain = args["domain"]

    if args.get("advanced", None):
        service.model.data.advanced = args["advanced"]

    service.saveAll()


def uninstall(job):
    service = job.service
    container = service.producers.get('container')[0]
    if container:
        j.tools.async.wrappers.sync(container.executeAction('stop', context=job.context))
        j.tools.async.wrappers.sync(container.delete())


def start(job):
    from zeroos.orchestrator.sal.Container import Container

    service = job.service
    container = service.producers.get('container')[0]
    if str(container.model.data.status) == 'halted':
        j.tools.async.wrappers.sync(container.executeAction('start', context=job.context))

    containerobj = Container.from_ays(container, job.context['token'])
    # setup resolv.conf
    containerobj.upload_content('/etc/resolv.conf', 'nameserver 127.0.0.1\n')

    # setup zerotier bridges
    setup_zerotierbridges(job)

    # setup cloud-init magical ip
    ip = containerobj.client.ip
    loaddresses = ip.addr.list('lo')
    magicip = '169.254.169.254/32'
    if magicip not in loaddresses:
        ip.addr.add('lo', magicip)

    restore_certificates(job, containerobj)
    # start services
    http = container.consumers.get('http')[0]
    dhcp = container.consumers.get('dhcp')[0]
    cloudinit = container.consumers.get('cloudinit')[0]
    firewall = container.consumers.get('firewall')[0]

    j.tools.async.wrappers.sync(container.executeAction('start', context=job.context))
    j.tools.async.wrappers.sync(dhcp.executeAction('start', context=job.context))
    j.tools.async.wrappers.sync(http.executeAction('start', context=job.context))
    j.tools.async.wrappers.sync(firewall.executeAction('start', context=job.context))
    j.tools.async.wrappers.sync(cloudinit.executeAction('start', context=job.context))
    save_certificates(job, containerobj)
    service.model.data.status = "running"


def stop(job):
    service = job.service
    container = service.producers.get('container')[0]
    if container:
        j.tools.async.wrappers.sync(container.executeAction('stop', context=job.context))
        service.model.data.status = "halted"


def setup_zerotierbridges(job):
    from zeroos.orchestrator.sal.Container import Container
    from zerotier import client
    import time

    service = job.service
    container = service.producers.get('container')[0]
    containerobj = Container.from_ays(container, job.context['token'])
    # get dict version of nics
    nics = service.model.data.to_dict()['nics']

    def wait_for_interface():
        start = time.time()
        while start + 60 > time.time():
            for link in containerobj.client.ip.link.list():
                if link['type'] == 'tun':
                    return
            time.sleep(0.5)
        raise j.exceptions.RuntimeError("Could not find zerotier network interface")

    ip = containerobj.client.ip
    for nic in nics:
        zerotierbridge = nic.pop('zerotierbridge', None)
        if zerotierbridge:
            nicname = nic['name']
            linkname = 'l-{}'.format(nicname)[:15]
            wait_for_interface()
            zerotiername = get_zerotier_nic(zerotierbridge['id'], containerobj)
            token = zerotierbridge.get('token')
            if token:
                zerotier = client.Client()
                zerotier.set_auth_header('bearer {}'.format(token))

                resp = zerotier.network.getMember(container.model.data.zerotiernodeid, zerotierbridge['id'])
                member = resp.json()

                job.logger.info("Enable bridge in member {} on network {}".format(member['nodeId'], zerotierbridge['id']))
                member['config']['activeBridge'] = True
                zerotier.network.updateMember(member, member['nodeId'], zerotierbridge['id'])

            # check if configuration is already done
            linkmap = {link['name']: link for link in ip.link.list()}

            if linkmap[nicname]['type'] == 'bridge':
                continue

            # bring related interfaces down
            ip.link.down(nicname)
            ip.link.down(zerotiername)

            # remove IP and rename
            ipaddresses = ip.addr.list(nicname)
            for ipaddress in ipaddresses:
                ip.addr.delete(nicname, ipaddress)
            ip.link.name(nicname, linkname)

            # create bridge and add interface and IP
            ip.bridge.add(nicname)
            ip.bridge.addif(nicname, linkname)
            ip.bridge.addif(nicname, zerotiername)

            # readd IP and bring interfaces up
            for ipaddress in ipaddresses:
                ip.addr.add(nicname, ipaddress)
            ip.link.up(nicname)
            ip.link.up(linkname)
            ip.link.up(zerotiername)

    service.model.data.zerotiernodeid = container.model.data.zerotiernodeid
    service.saveAll()
