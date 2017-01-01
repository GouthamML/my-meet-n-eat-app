from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import DATETIME
from sqlalchemy.orm import relationship, sessionmaker
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
import re
import random, string


Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
    	s = Serializer(secret_key, expires_in = expiration)
    	return s.dumps({'id': self.id })


    @staticmethod
    def verify_auth_token(token):
    	s = Serializer(secret_key)
    	try:
    		data = s.loads(token)
    	except SignatureExpired:
    		#Valid Token, but expired
    		return None
    	except BadSignature:
    		#Invalid Token
    		return None
    	user_id = data['id']
    	return user_id


class Request(Base):
    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    meal_type = Column(String(32))
    location_string = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    meal_time = Column(DATETIME)
    filled = Column(Boolean, unique=False, default=True)


class Proposal(Base):
    __tablename__= 'proposal'
    id = Column(Integer, primary_key=True)
    user_proposed_to = Column(String)
    user_proposed_from = Column(String)
    request_id = Column(Integer, ForeignKey('request.id'))
    filled = Column(Boolean, unique=False, default=True)


class MealDate(Base):
    __tablename__= 'mealdate'
    id = Column(Integer, primary_key=True)
    user_id_1 = Column(Integer, ForeignKey('user.id'))
    user_id_2 = Column(Integer, ForeignKey('user.id'))
    restaurant_name = Column(String)
    restaurant_addres = Column(String)
    restaurant_picture = Column(String)

    @property
    def get_meal_time(self):
        pass
