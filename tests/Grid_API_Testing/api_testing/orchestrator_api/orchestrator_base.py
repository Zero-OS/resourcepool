from zeroos.orchestrator import client as apiclient
from testconfig import config

api_base_url = config['main']['api_base_url']
client_id = config['main']['client_id']
client_secret = config['main']['client_secret']
organization = config['main']['organization']


class GridPyclientBase(object):
    def __init__(self):
        self.jwt = self.get_jwt()
        self.api_client = apiclient.APIClient(api_base_url)
        self.api_client.set_auth_header("Bearer %s" % self.jwt)

    def get_jwt(self):
        auth = apiclient.oauth2_client_itsyouonline.Oauth2ClientItsyouonline()
        response = auth.get_access_token(client_id, client_secret, scopes=['user:memberof:%s' % organization], audiences=[])
        return response.content.decode('utf-8')
