def install(job):
    gateway = job.service.parent.consumers['gateway'][0]
    gwdata = gateway.model.data.to_dict()

    cloudinit = config_cloud_init(job, gwdata.get("nics", []))
    if not cloudinit.is_running():
        cloudinit.start()


def config_cloud_init(job, nics=None):
    import json
    from zeroos.restapi.sal.gateway.cloudinit import CloudInit
    from zeroos.restapi.sal.Container import Container

    container = Container.from_ays(job.service.parent)
    nics = nics or []
    config = {}

    for nic in nics:
        if not nic.get("dhcpserver"):
            continue

        for host in nic["dhcpserver"].get("hosts", []):
            if host.get("cloudinit"):
                if host["cloudinit"]["userdata"] and host["cloudinit"]["metadata"]:
                    userdata = json.loads(host["cloudinit"]["userdata"])
                    metadata = json.loads(host["cloudinit"]["metadata"])
                    config[host['macaddress'].lower()] = json.dumps({
                        "meta-data": metadata,
                        "user-data": userdata,
                    })

    cloudinit = CloudInit(container, config)
    if config != {}:
        cloudinit.apply_config()
    return cloudinit


def update(job):
    if job.model.args.get("nics", None):
        config_cloud_init(job, job.model.args["nics"])
