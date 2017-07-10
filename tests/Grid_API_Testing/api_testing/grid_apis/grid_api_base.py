import requests
from testconfig import config


class GridAPIBase(object):
    def __init__(self):
        self.config = config['main']
        self.api_base_url = self.config['api_base_url']
        self.headers = {'content-type': 'application/json'}
        self.requests = requests

    def request_api(self, method, api, body='', params=''):
        if method not in ['post', 'get', 'put', 'delete']:
            raise NameError(" [*] %s method isn't handled" % method)

        api = self.build_api(api)

        if method == 'get':
            response = self.requests.get(url=api, headers=self.headers, params=params)
        elif method == 'post':
            response = self.requests.post(url=api, headers=self.headers, json=body, params=params)

        elif method == 'put':
            response = self.requests.put(url=api, headers=self.headers, json=body, params=params)
        elif method == 'delete':
            response = self.requests.delete(url=api, json=body, headers=self.headers,params = params)

        return response

    def build_api(self, api):
        api_path = self.api_base_url
        if api_path[-1] != '/':
            api_path += '/'

        for item in api:
            api_path += item + '/'

        return api_path[:-1]
