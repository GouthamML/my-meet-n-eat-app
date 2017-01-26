import os
import random, string

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'app.db'))
DATABASE_CONNECT_OPTIONS = {}
SEND_FILE_MAX_AGE_DEFAULT = 0
OAUTH_CREDENTIALS = {
                    'google': {
                        'id': '1080912678595-adm52eo5f78jru65923qia22itfasa7d.apps.googleusercontent.com',
                        'secret': '1vq9zxw2rMiBtUVeLlAlNOVw'
                    }
                    }
ASSETS_DEBUG = True
TEMPLATES_AUTO_RELOAD = True
UPLOADS_DEFAULT_DEST = BASE_DIR+'/static/img/profile/'
UPLOADS_DEFAULT_URL = 'http://0.0.0.0:8000/register'
UPLOADED_PHOTOS_DEST = BASE_DIR+'/static/img/profile/'
UPLOADED_PHOTOS_URL = 'http://0.0.0.0:8000/register'