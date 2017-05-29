def install(job):
    gateway = job.service.parent.consumers['gateway'][0]
    gwdata = gateway.model.data.to_dict()
    apply_rules(job, gwdata)


def apply_rules(job, gwdata=None):
    from zeroos.restapi.sal.Container import Container
    from zeroos.restapi.sal.gateway.firewall import Firewall, Network

    gwdata = {} if gwdata is None else gwdata
    container = Container.from_ays(job.service.parent)
    portforwards = gwdata.get('portforwards', [])
    # lets assume the public ip is the ip of the nic which has a gateway configured

    publicnetwork = None
    privatenetworks = []
    for nic in gwdata["nics"]:
        if nic["config"]:
            if nic["config"].get("gateway", None):
                publicnetwork = Network(nic["name"], nic["config"]["cidr"])
            else:
                privatenetworks.append(Network(nic["name"], nic["config"]["cidr"]))
    firewall = Firewall(container, publicnetwork, privatenetworks, portforwards)
    firewall.apply_rules()


def update(job):
    if job.model.args.get("nics", None):
        apply_rules(job, job.model.args)
