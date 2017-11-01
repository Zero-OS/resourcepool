

def processChange(job):
    service = job.service
    args = job.model.args
    if args.pop('changeCategory') != 'dataschema':
        return

    if 'url' in args:
        service.model.data.url = args['url']
    if 'eventtypes' in args:
        service.model.data.eventtypes = args['eventtypes']

    service.saveAll()
