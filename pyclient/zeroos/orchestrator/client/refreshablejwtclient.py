from .client import Client
import time
import requests
RENEWAL_TIME=20*60

class RefreshingJWTClient(Client):

    def __init__(self, *args, **kwargs):
        self._last_jwt_update = 0
        super(RefreshingJWTClient, self).__init__(*args, **kwargs)

    def _get_headers(self, headers, content_type):
        if self._last_jwt_update + RENEWAL_TIME < time.time():
            self._refresh_jwt_token()            
        return super(RefreshingJWTClient, self)._get_headers(headers, content_type)

    def set_refreshable_jwt(self, jwt, timeout):
        self._jwt = jwt
        self._timeout = timeout

    def _refresh_jwt_token(self):
        if not self._jwt:
            raise ValueError("Refreshable JWT is not set")
        headers = {'Authorization': 'bearer {}'.format(self._jwt)}
        params = {'validity': str(self._timeout)}
        resp = requests.get('https://itsyou.online/v1/oauth/jwt/refresh', headers=headers, params=params)
        resp.raise_for_status()
        new_jwt = resp.content.decode()
        self.set_auth_header('Bearer %s' % new_jwt)
        self._last_jwt_update = time.time()

