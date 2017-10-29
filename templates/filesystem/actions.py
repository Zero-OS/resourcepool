from js9 import j


def input(job):
    if job.model.args.get("mountpoint", "") != "":
        raise j.exceptions.Input("Mountpoint should not be set as input")
    if job.model.args.get("name", "") == "":
        raise j.exceptions.Input("Filesystem requires a name")


def get_pool(job):
    from zeroos.orchestrator.configuration import get_jwt_token
    from zeroos.orchestrator.sal.Node import Node

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    nodeservice = job.service.parent.parent
    poolname = job.service.parent.name
    node = Node.from_ays(nodeservice, job.context['token'])
    return node.storagepools.get(poolname)


def install(job):
    pool = get_pool(job)
    fsname = str(job.service.model.data.name)
    try:
        fs = pool.get(fsname)
    except ValueError:
        fs = pool.create(fsname, int(job.service.model.data.quota * 1024 * 1024))
    job.service.model.data.mountpoint = fs.path


def delete(job):
    pool = get_pool(job)
    fsname = str(job.service.model.data.name)
    try:
        fs = pool.get(fsname)
    except ValueError:
        return
    fs.delete()


def update_sizeOnDisk(job):
    return False


def monitor(job):
    service = job.service

    if service.model.actionsState['install'] != 'ok':
        return

    pool = get_pool(job)
    for device in pool.fsinfo['devices']:
        usage_precentage = (device.get('used')/device.get('size'))*100
        if usage_precentage == 90:
            service.model.data.status = 'warning'
        elif usage_precentage > 99:
            service.model.data.status = 'error'
            raise RuntimeError('Filesystem  %s disk  is full !' % service.name)
        else:
            pass
