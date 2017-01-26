from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
import json

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('users.oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GoogleSignIn(OAuthSignIn):
    """docstring for """
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
        name='google',
        client_id=self.consumer_id,
        client_secret=self.consumer_secret,
        base_url='https://www.googleapis.com/oauth2/v1/',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='https://www.googleapis.com/auth/userinfo.email',
            response_type='code',
            access_type ='offline',
            redirect_uri=self.get_callback_url()),
        )

    def callback(self):
        if 'code' not in request.args :
            return None, None, None, None
        code = request.args['code']
        print 'code -> ', code

        payload = {
         'grant_type': 'authorization_code',
          'code': code,
           'scope':'https://www.googleapis.com/auth/userinfo.email',
           'redirect_uri':self.get_callback_url()
        }
        access_token = self.service.get_access_token(decoder=json.loads, data=payload)

        print 'access_token ->', access_token

        oauth_session = self.service.get_session(access_token)
        me = oauth_session.get('userinfo').json()
        print me
        social_id = 'google$' + me.get('id')
        username = me.get('email').split('@')[0]
        picture = me.get('picture')
        email = me.get('email')
        return social_id, username, email, picture