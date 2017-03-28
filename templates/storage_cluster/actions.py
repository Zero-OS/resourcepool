from JumpScale import j


def install(job):
    service = job.parent.service
    node = j.sal.g8os.get_node(
        addr=service.model.data.redisaddr,
        port=service.model.data.redisport,
        password=service.model.data.redispassword or None,
    )

def delete(job):
    raise NotImplementedError()

def addStorageServer(job):
    raise NotImplementedError()

def reoveStorageServer(job):
    raise NotImplementedError()
