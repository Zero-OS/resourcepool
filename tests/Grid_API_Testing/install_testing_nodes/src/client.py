import requests
import os

'''
Shameless stolen from
https://github.com/Jumpscale/jumpscale_core8/blob/master/lib/JumpScale/clients/portal/PortalClient.py
'''


class ApiError(Exception):
    def __init__(self, response):
        msg = '%s %s' % (response.status_code, response.reason)
        try:
            message = response.json()
        except:
            message = response.content
        if isinstance(message, (str, bytes)):
            msg += '\n%s' % message
        elif isinstance(message, dict) and 'errormessage' in message:
            msg += '\n%s' % message['errormessage']

        super(ApiError, self).__init__(msg)
        self._response = response

    @property
    def response(self):
        return self._response


class BaseResource:
    def __init__(self, session, url):
        self._session = session
        self._url = url

    def __getattr__(self, item):
        url = os.path.join(self._url, item)
        resource = BaseResource(self._session, url)
        setattr(self, item, resource)
        return resource

    def __call__(self, **kwargs):
        response = self._session.post(self._url, kwargs)

        if not response.ok:
            raise ApiError(response)

        if response.headers.get('content-type', 'text/html') == 'application/json':
            return response.json()

        return response.content


class Client(BaseResource):
    def __init__(self, baseurl, login, password):
        session = requests.Session()
        url = "%s/%s" % (baseurl, '/restmachine')
        BaseResource.__init__(self,session, url)
        self.system.usermanager.authenticate(name=login, secret=password)

