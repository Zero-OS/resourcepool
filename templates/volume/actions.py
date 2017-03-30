def get_node_client(service):
    node = service.producers['node'][0]
    return j.clients.g8core.get(host=node.model.data.redisAddr,
                                port=node.model.data.redisPort,
                                password=node.model.data.redisPassword)

def get_container_client(service, id):
    client = get_node_client(service)
    return client.container.client(id)

def create_container(service):
    client = get_node_client(service)
    id = client.container.create(
        'https://hub.gig.tech/maxux/flist-gonbdserver.flist',
        host_network=True,
        storage='ardb://hub.gig.tech:16379')
    service.model.data.containerId = id
    return get_container_client(service, id)

def install(job):
    service = job.service
    container = create_container(service)
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
    service.model.data.status = 'running'

def start(job):
    service = job.service
    j.tools.async.wrappers.sync(service.executeAction('install'))

def pause(job):
    service = job.service
    client = get_container_client(job.service, service.model.data.containerId)
    for proc in client.process.list():
        if service.model.key in proc['cmd']['arguments']['args']:
            client.process.kill(proc['cmd']['id'])
    service.model.data.status = 'halted'

def rollback(job):
    service = job.service
    service.model.data.status = 'rollingback'
    # TODO: rollback disk
    service.model.data.status = 'running'

def resize(job):
    service = job.service
    job.logger.info("resize volume {}".format(service.name))

    if 'size' not in job.model.args:
        raise j.exceptions.Input("size is not present in the arguments of the job")

    size = int(job.model.args['size'])
    if size < service.model.data.size:
        raise j.exceptions.Input("size is smaller then current size, disks can grown")

    service.model.data.size = size

def processChange(job):
    service = job.service

    args = job.model.args
    category = args.pop('changeCategory')
    if category == "dataschema" and service.model.actionsState['install'] == 'ok':
        j.tools.async.wrappers.sync(service.executeAction('resize', args={'size': args['size']}))
