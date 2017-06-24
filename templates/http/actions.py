def start(job):
    gateway = job.service.parent.consumers['gateway'][0]
    gwdata = gateway.model.data.to_dict()
    httpproxies = gwdata.get('httpproxies', [])
    apply_rules(job, httpproxies)


def apply_rules(job, httpproxies=None):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.gateway.http import HTTPServer

    container = Container.from_ays(job.service.parent, job.context['token'])

    httpproxies = [] if httpproxies is None else httpproxies

    # for cloud init we we add some proxies specially for cloud-init
    httpproxies.append({
        'host': '169.254.169.254',
        'destinations': ['http://127.0.0.1:8080'],
        'types': ['http']}
    )

    http = HTTPServer(container, httpproxies)
    http.apply_rules()


def update(job):
    apply_rules(job, job.model.args["httpproxies"])
