# coding=utf-8
from flask import Flask
from flask_wtf import CsrfProtect
from models import Base, engine
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)
csrf = CsrfProtect()

app.config['OAUTH_CREDENTIALS'] = {
      'google': {
          'id': '1080912678595-adm52eo5f78jru65923qia22itfasa7d.apps.googleusercontent.com',
          'secret': '1vq9zxw2rMiBtUVeLlAlNOVw'
      }
}

csrf.init_app(app)

from app import models, views
