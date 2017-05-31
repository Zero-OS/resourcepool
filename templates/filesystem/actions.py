from js9 import j


def input(job):
    if job.model.args.get("mountpoint", "") != "":
        raise j.exceptions.Input("Mountpoint should not be set as input")
    if job.model.args.get("name", "") == "":
        raise j.exceptions.Input("Filesystem requires a name")


def get_pool(service):
    from zeroos.orchestrator.sal.Node import Node
    nodeservice = service.parent.parent
    poolname = service.parent.name
    node = Node.from_ays(nodeservice)
    return node.storagepools.get(poolname)


def install(job):
    pool = get_pool(job.service)
    fsname = str(job.service.model.data.name)
    try:
        fs = pool.get(fsname)
    except ValueError:
        fs = pool.create(fsname, int(job.service.model.data.quota))
    job.service.model.data.mountpoint = fs.path


def delete(job):
    pool = get_pool(job.service)
    fsname = str(job.service.model.data.name)
    try:
        fs = pool.get(fsname)
    except ValueError:
        return
    fs.delete()


def update_sizeOnDisk(job):
    return False
