# coding=utf-8
from flask import Flask
from flask_wtf import CsrfProtect
from config import DevelopmentConfig
from models import Base, engine
from assets import create_assets
from flask_assets import Environment
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CsrfProtect()
assets = Environment(app)
create_assets(assets)


csrf.init_app(app)

from app import models, views, config, assets
