from JumpScale import j


def input(job):
    if job.model.args.get("mountpoint", "") != "":
        raise j.exceptions.Input("Mountpoint should not be set as input")
    if job.model.args.get("name", "") == "":
        raise j.exceptions.Input("Filesystem requires a name")


def get_pool(service):
    nodeservice = service.parent.parent
    poolname = service.parent.name
    node = j.sal.g8os.get_node(
        addr=nodeservice.model.data.redisAddr,
        port=nodeservice.model.data.redisPort,
        password=nodeservice.model.data.redisPassword or None,
    )
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
