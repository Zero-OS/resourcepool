from js9 import j


def init_actions_(service, args):
    return {
        'init': [],
        'install': ['init'],
        'delete': [],
    }


def input(job):
    if job.model.args.get("path", "") != "":
        raise j.exceptions.Input("path should not be set as input")


def get_filesystem(job):
    from zeroos.orchestrator.sal.Node import Node
    nodeservice = job.service.parent.parent.parent
    poolname = job.service.parent.parent.name
    fsname = str(job.service.parent.model.data.name)
    node = Node.from_ays(nodeservice, job.context['token'])
    pool = node.storagepools.get(poolname)
    return pool.get(fsname)


def install(job):
    name = str(job.service.model.data.name)
    fs = get_filesystem(job)
    try:
        snap = fs.get(name)
    except ValueError:
        snap = fs.create(name)

    job.service.model.data.path = snap.path


def delete(job):
    name = str(job.service.model.data.name)
    fs = get_filesystem(job)
    snapshot = fs.get(name)
    snapshot.delete()


def rollback(job):
    name = str(job.service.model.data.name)
    fs = get_filesystem(job)
    snapshot = fs.get(name)
    snapshot.rollback()


def monitor(job):
    pass
