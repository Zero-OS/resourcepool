def install(job):
    gateway = job.service.parent.consumers['gateway'][0]
    gwdata = gateway.model.data.to_dict()
    httpproxies = gwdata.get('httpproxies', [])
    nics = gwdata.get('nics', [])
    apply_rules(job, httpproxies, nics)


def apply_rules(job, httpproxies=None, nics=None):
    import ipaddress
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.gateway.http import HTTPServer

    container = Container.from_ays(job.service.parent)

    httpproxies = [] if httpproxies is None else httpproxies
    nics = [] if nics is None else nics

    # we add some proxies specially for cloud-init
    for nic in nics:
        dhcpconfig = nic.get('dhcpserver')
        if dhcpconfig and 'config' in nic and nic['config']['cidr']:
            gwip = str(ipaddress.IPv4Interface(nic['config']['cidr']).ip)
            httpproxies.append({
                'host': gwip,
                'destinations': ['http://127.0.0.1:8080'],
                'types': ['http']}
            )

    http = HTTPServer(container, httpproxies)
    http.apply_rules()


def update(job):
    apply_rules(job, job.model.args["httpproxies"], job.model.args["nics"])
