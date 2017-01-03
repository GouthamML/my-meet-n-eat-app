# coding=utf-8
from flask import Flask
from flask_wtf import CsrfProtect
from models import Base, engine
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

app = Flask(__name__)
csrf = CsrfProtect()

if not database_exists(engine.url):
    create_database(engine.url)

csrf.init_app(app)

with app.app_context():
    Base.metadata.create_all(engine)

from app import models, views
