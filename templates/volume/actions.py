def install(job):
    service = job.service
    service.model.data.status = 'halted'

def start(job):
    service = job.service
    service.model.data.status = 'running'

def pause(job):
    service = job.service
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
