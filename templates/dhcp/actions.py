def start(job):
    gateway = job.service.parent.consumers['gateway'][0]
    gwdata = gateway.model.data.to_dict()
    apply_config(job, gwdata)


def apply_config(job, gwdata=None):
    import ipaddress
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.gateway.dhcp import DHCP

    container = Container.from_ays(job.service.parent, job.context['token'])

    gwdata = {} if gwdata is None else gwdata
    nics = gwdata.get('nics', [])
    dhcpservers = []

    for nic in nics:
        dhcpserver = nic.get('dhcpserver')
        if not dhcpserver:
            continue

        cidr = ipaddress.IPv4Interface(nic['config']['cidr'])
        dhcpserver['subnet'] = str(cidr.network.network_address)
        dhcpserver['gateway'] = str(cidr.ip)
        dhcpserver['interface'] = nic['name']
        dhcpservers.append(dhcpserver)

    dhcp = DHCP(container, gwdata['domain'], dhcpservers)
    dhcp.apply_config()


def update(job):
    apply_config(job, job.model.args)


def watchdog_handler(job):
    gateway = job.service.parent.consumers['gateway'][0]
    if gateway.model.status == 'running':
        start(job)
