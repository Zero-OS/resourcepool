from JumpScale import j

def init_actions_(service, args):
    return {
        'init': [],
        'install': ['init'],
        'delete': [],
    }

def input(job):
    if job.model.args.get("path", "") != "":
        raise j.exceptions.Input("path should not be set as input")


def get_filesystem(service):
    nodeservice = service.parent.parent.parent
    poolname = service.parent.parent.name
    fsname = str(service.parent.model.data.name)
    node = j.sal.g8os.get_node(
        addr=nodeservice.model.data.redisAddr,
        port=nodeservice.model.data.redisPort,
        password=nodeservice.model.data.redisPassword or None,
    )
    pool = node.storagepools.get(poolname)
    return pool.get(fsname)


def install(job):
    name = str(job.service.model.data.name)
    fs = get_filesystem(job.service)
    try:
        snap = fs.get(name)
    except ValueError:
        snap = fs.create(name)

    job.service.model.data.path = snap.path


def delete(job):
    name = str(job.service.model.data.name)
    fs = get_filesystem(job.service)
    snapshot = fs.get(name)
    snapshot.delete()


def rollback(job):
    name = str(job.service.model.data.name)
    fs = get_filesystem(job.service)
    snapshot = fs.get(name)
    snapshot.rollback()
