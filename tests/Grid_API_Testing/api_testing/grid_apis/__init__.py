from zeroos.orchestrator import client as apiclient
from testconfig import config

def get_jwt():
    auth = apiclient.oauth2_client_itsyouonline.Oauth2ClientItsyouonline()
    response = auth.get_access_token(client_id, client_secret, scopes=['user:memberof:%s' % organization], audiences=[])
    return response.content.decode('utf-8')

api_base_url = config['main']['api_base_url']
client_id = config['main']['client_id']
client_secret = config['main']['client_secret']
organization = config['main']['organization']    
    
JWT = get_jwt()