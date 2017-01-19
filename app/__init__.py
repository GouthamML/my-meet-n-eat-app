# coding=utf-8
from flask import Flask
from flask_wtf import CsrfProtect
from flask_login import LoginManager
from config import DevelopmentConfig
from models import Base, engine
from assets import create_assets
from flask_assets import Environment
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask_uploads import UploadSet, configure_uploads, IMAGES

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
profile_photo = UploadSet('photos', IMAGES)
configure_uploads(app, profile_photo)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
csrf = CsrfProtect()
assets = Environment(app)
create_assets(assets)
csrf.init_app(app)
Base.metadata.create_all(engine)

from app import models, views, config, assets
