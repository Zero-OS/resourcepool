def get_node_client(service):
    node = service.parent.parent
    return j.clients.g8core.get(host=node.model.data.redisAddr,
                                port=node.model.data.redisPort,
                                password=node.model.data.redisPassword)

def get_container_client(service):
    client = get_node_client(service)
    return client.container.client(service.parent.model.data.id)

def is_running(client, key):
    try:
        for process in client.process.list():
            if process['cmd']['arguments']['name'] == '/nbdserver' and \
               '-export {}'.format(key) in process['cmd']['arguments']['args']:
                return process
        return False
    except Exception as err:
        if str(err).find("invalid container id"):
            return False
        raise

def install(job):
    service = job.service
    container = get_container_client(service)
    # client.system(
    #     '/nbdserver \
    #     -protocol unix \
    #     -address "/server.socket.{id}" \
    #     -export {id} \
    #     -backendcontroller {api} \
    #     -volumecontroller {api}'
    #     .format(id=service.model.key, api=service.model.data.gridApiUrl)
    # )
    # FIXME: update when the change on the nbd server for grid API are done.
    container.system(
        '/nbdserver \
        -protocol unix \
        -address "/server.socket.{id}" \
        -export {id}'
        .format(id=service.model.key))

    service.model.data.socketPath = '/server.socket.{id}'.format(id=service.model.key)

def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))

def stop(job):
    import time
    service = job.service
    client = get_container_client(service=service)
    process = is_running(client, service.model.key)
    if process:
        job.logger.info("killing process {}".format(process['cmd']['arguments']['name']))
        client.process.kill(process['cmd']['id'])

        job.logger.info("wait for nbdserver to stop")
        for i in range(60):
            time.sleep(1)
            if is_running(client, service.model.key):
                continue
            return
        raise j.exceptions.RuntimeError("ardb-server didn't stopped")
