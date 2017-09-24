def start(job):
    gateway = job.service.parent.consumers['gateway'][0]
    gwdata = gateway.model.data.to_dict()
    httpproxies = gwdata.get('httpproxies', [])
    apply_rules(job, httpproxies)


def apply_rules(job, httpproxies=None):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.gateway.http import HTTPServer
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    container = Container.from_ays(job.service.parent, job.context['token'], logger=job.service.logger)

    httpproxies = [] if httpproxies is None else httpproxies

    # for cloud init we we add some proxies specially for cloud-init
    # this will only take effect with the (http) type
    httpproxies.append({
        'host': '169.254.169.254',
        'destinations': ['http://127.0.0.1:8080'],
        'types': ['http']}
    )

    service = job.service
    http = HTTPServer(container, service, httpproxies)
    http.apply_rules()


def update(job):
    apply_rules(job, job.model.args["httpproxies"])


def watchdog_handler(job):
    import asyncio

    loop = j.atyourservice.server.loop
    gateway = job.service.parent.consumers['gateway'][0]
    if gateway.model.data.status == 'running':
        asyncio.ensure_future(job.service.executeAction('start', context=job.context), loop=loop)
