# coding=utf-8
from flask import Flask
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_assets import Environment
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import CSRFProtect
from users.models import Base, engine
from sqlalchemy.ext.declarative import declarative_base

from assets import create_assets

app = Flask(__name__)

app.config.from_object('config')
profile_photo = UploadSet('photos', IMAGES)
configure_uploads(app, profile_photo)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
csrf = CSRFProtect()
assets = Environment(app)
create_assets(assets)
csrf.init_app(app)
Base.metadata.create_all(engine)


from app.users.views import mod as usersModule
app.register_blueprint(usersModule)