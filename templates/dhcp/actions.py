from js9 import j


def start(job):
    gateway = job.service.parent.consumers['gateway'][0]
    gwdata = gateway.model.data.to_dict()
    apply_config(job, gwdata)


def apply_config(job, gwdata=None):
    import ipaddress
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.gateway.dhcp import DHCP
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    container = Container.from_ays(job.service.parent, job.context['token'], logger=job.service.logger)

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


def monitor(job):
    import asyncio

    loop = j.atyourservice.server.loop
    gateway = job.service.parent.consumers['gateway'][0]
    if gateway.model.data.status == 'running':
        asyncio.ensure_future(job.service.executeAction('start', context=job.context), loop=loop)
