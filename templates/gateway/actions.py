from JumpScale import j


def input(job):
    import ipaddress

    domain = job.model.args.get('domain')
    if not domain:
        raise j.exceptions.Input('Domain cannot be empty.')

    nics = job.model.args.get('nics', [])
    publicnetwork = False
    privatenetwork = False
    for nic in nics:
        config = nic.get('config', {})
        name = nic.get('name')
        dhcp = nic.get('dhcpserver')
        cidr = config.get('cidr')

        if not name:
            raise j.exceptions.Input('Gateway nic should have name defined.')

        if config:
            if config.get('gateway'):
                publicnetwork = True
                if dhcp:
                    raise j.exceptions.Input('DHCP can only be defined for private networks')
            else:
                privatenetwork = True

        if dhcp:
            if not cidr:
                raise j.exceptions.Input('Gateway nic should have cidr if a DHCP server is defined.')
            nameservers = dhcp.get('nameservers')

            if not nameservers:
                raise j.exceptions.Input('DHCP nameservers should have at least one nameserver.')
            hosts = dhcp.get('hosts')
            subnet = ipaddress.IPv4Interface(cidr).network
            for host in hosts:
                ip = host.get('ipaddress')
                if not ip or not ipaddress.ip_address(ip) in subnet:
                    raise j.exceptions.Input('Dhcp host ipaddress should be within cidr subnet.')

    if not publicnetwork:
        raise j.exceptions.Input("Gateway should have at least one Public Address (gw defined)")
    if not privatenetwork:
        raise j.exceptions.Input("Gateway should have at least one Private Address (no gw defined)")
    return job.model.args


def init(job):
    service = job.service
    containeractor = service.aysrepo.actorGet("container")
    nics = service.model.data.to_dict()['nics']  # get dict version of nics
    for nic in nics:
        if 'dhcpserver' in nic:
            nic.pop('dhcpserver')

    args = {
        'node': service.model.data.node,
        'flist': 'https://hub.gig.tech/gig-official-apps/g8osgw.flist',
        'nics': nics,
        'hostname': service.model.data.hostname,
        'hostNetworking': False,
    }
    cont_service = containeractor.serviceCreate(instance=service.name, args=args)
    service.consume(cont_service)

    args = {
        'container': service.name
    }

    # create firewall
    fwactor = service.aysrepo.actorGet('firewall')
    fw_service = fwactor.serviceCreate(instance=service.name, args=args)
    fw_service.consume(cont_service)

    # create http
    httpactor = service.aysrepo.actorGet('http')
    http_service = httpactor.serviceCreate(instance=service.name, args=args)
    http_service.consume(cont_service)

    # create dhcp
    dhcpactor = service.aysrepo.actorGet('dhcp')
    dhcp_service = dhcpactor.serviceCreate(instance=service.name, args=args)
    dhcp_service.consume(cont_service)

    # Start cloudinit
    cloudinitactor = service.aysrepo.actorGet("cloudinit")
    cloudinit_service = cloudinitactor.serviceCreate(instance=service.name, args=args)
    cloudinit_service.consume(cont_service)


def install(job):
    service  = job.service
    j.tools.async.wrappers.sync(service.executeAction('start'))


def processChange(job):
    service = job.service
    args = job.model.args
    category = args.pop('changeCategory')

    if category != 'dataschema':
        return

    service.model.data.portforwards = args.get('portforwards', service.model.data.portforwards)

    if service.model.data.nics != args.get('nics', service.model.data.nics):
        cloudInitServ = service.aysrepo.serviceGet(role='cloudinit', instance=service.name)
        j.tools.async.wrappers.sync(cloudInitServ.executeAction('update', args={'nics': args['nics']}))

        firewallServ = service.aysrepo.serviceGet(role='firewall', instance=service.name)
        j.tools.async.wrappers.sync(firewallServ.executeAction('update', args={'data': args}))

        dhcpServ = service.aysrepo.serviceGet(role='dhcp', instance=service.name)
        j.tools.async.wrappers.sync(dhcpServ.executeAction('update', args={'data': args}))

        service.model.data.nics = args['nics']

    if args.get("httpproxies", None):
        httpServ = service.aysrepo.serviceGet(role='http', instance=service.name)
        http_args = {'httpproxies': args["httpproxies"], 'nics': args.get('nics', service.model.data.nics)}
        j.tools.async.wrappers.sync(httpServ.executeAction('update', args=http_args))
        service.model.data.httpproxies = args['httpproxies']

    if args.get("advanced", None):
        service.model.data.advanced = args["advanced"]

def uninstall(job):
    service = job.service
    container = service.producers.get('container')[0]
    if container:
        j.tools.async.wrappers.sync(container.executeAction('stop'))
        j.tools.async.wrappers.sync(container.delete())

def start(job):
    service = job.service
    container = service.producers.get('container')[0]
    http = container.consumers.get('http')[0]
    dhcp = container.consumers.get('dhcp')[0]
    cloudinit = container.consumers.get('cloudinit')[0]
    firewall = container.consumers.get('firewall')[0]

    j.tools.async.wrappers.sync(container.executeAction('start'))
    j.tools.async.wrappers.sync(http.executeAction('install'))
    j.tools.async.wrappers.sync(dhcp.executeAction('install'))
    j.tools.async.wrappers.sync(firewall.executeAction('install'))
    j.tools.async.wrappers.sync(cloudinit.executeAction('install'))

def stop(job):
    service = job.service
    container = service.producers.get('container')[0]
    if container:
        j.tools.async.wrappers.sync(container.executeAction('stop'))
