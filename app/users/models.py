from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum, create_engine, Float, func, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import DATE, TIME, DATETIME
from sqlalchemy.orm import relationship, sessionmaker
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from flask_login import UserMixin
from config import BASE_DIR
import os
import random, string
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
engine = create_engine('sqlite:///{}'.format(os.path.join(BASE_DIR, 'app.db')))
DBSession = sessionmaker(bind=engine)
session = DBSession()


secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


class BaseModel(Base):
    __abstract__  = True
    id            = Column(Integer, primary_key=True)
    date_created  = Column(DATETIME,  default=func.current_timestamp())
    date_modified = Column(DATETIME,  default=func.current_timestamp(),
                                           onupdate=func.current_timestamp())


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    def set_email(self, email):
        self.email = email

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

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         return {
            "id" : self.id,
            "username": self.username,
            "picture" : self.picture
            }


class ProfileImage(BaseModel):
    __tablename__= 'image_profile'
    user_id =  Column(Integer, ForeignKey('user.id'))
    image_filename = Column(String, default=None, nullable=True)
    image_url = Column(String, default=None, nullable=True)


class OAuthMembership(Base):
    """docstring for """
    __tablename__ = 'oauthmembership'
    provider = Column(String(30), primary_key=True)
    provider_userid =  Column(String(100), primary_key=True)
    user_id =  Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         return {
         "provider" : self.provider,
         "provideruserid": self.provider_userid
         }


class Request(BaseModel):
    __tablename__ = 'request'
    user_id = Column(Integer, ForeignKey('user.id'))
    meal_type = Column(String(32))
    location_string = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    filled = Column(Boolean, unique=False, default=False)

    @property
    def get_date_time(self):
        return session.query(DateTimeRequest).filter_by(request=self.id).first()

    @hybrid_property
    def edit_meal_type(self):
        return self.meal_type

    @edit_meal_type.setter
    def edit_meal_type(self, value):
        self.meal_type = value

    @hybrid_property
    def edit_location_string(self):
        return self.location_string

    @edit_location_string.setter
    def edit_location_string(self, value):
        self.location_string = value

    @hybrid_property
    def edit_latitude(self):
        return self.latitude

    @edit_latitude.setter
    def edit_latitude(self, value):
        self.latitude = value

    @hybrid_property
    def edit_longitude(self):
        return self.longitude

    @edit_longitude.setter
    def edit_longitude(self, value):
        self.longitude = value

    @property
    def serialize(self):
         """Return object data in easily serializeable format"""
         request_datetime = session.query(DateTimeRequest).filter_by(request = self.id).first()

         return {
         "id" : self.id,
         "filled": self.filled,
         "meal_type": self.meal_type,
         "longitude": self.longitude,
         "latitude": self.latitude,
         "location_string": self.location_string,
         "meal_time": request_datetime.mealtime,
         "date": str(request_datetime.date)
         }

    @staticmethod
    def validate(data):
        errors = []
        required_fields = ['meal_type','longitude', 'latitude', 'location_string']
        if type(data) != dict:
            error = dict({"Missing required parameters":" ".format(', '.join(required_fields))})
            errors.append(error)
        else:
            for value in required_fields:
                if not value in data:
                    error = dict({ value: "Required" })
                    errors.append(error)
                else:
                    if not data[value]:
                        error = dict({ value: "Required" })
                        errors.append(error)
        return errors

class DateTimeRequest(BaseModel):
    __tablename__='datetimemeal'
    request = Column(Integer, ForeignKey('request.id'))
    mealtime = Column(Enum('breakfast', 'lunch', 'afternoon snack', 'dinner'))
    date = Column(DATE)


class Proposal(BaseModel):
    __tablename__= 'proposal'
    user_proposed_to = Column(Integer, ForeignKey('user.id'))
    user_proposed_from = Column(Integer, ForeignKey('request.user_id'))
    request_id = Column(Integer, ForeignKey('request.id'))
    filled = Column(Boolean, unique=False, default=False)

    @property
    def get_request_data(self):
         r = session.query(Request).filter_by(id=self.request_id).first()
         return {
           'meal_type': r.meal_type,
       	   'location': r.location_string,
           'latitude': r.latitude,
           'longitude': r.longitude
         }
        
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        "id" : self.id,
        "filled": self.filled,
        "request_id": self.request_id,
        "user_proposed_to": self.user_proposed_to,
        "user_proposed_from": self.user_proposed_from,
        }

    @staticmethod
    def validate(data):
        errors = []
        required_fields = ['request_id']
        if type(data) != dict:
            error = dict({"Missing required parameters":" ".format(', '.join(required_fields))})
            errors.append(error)
        else:
            for value in required_fields:
                if not value in data:
                    error = dict({ value: "Required" })
                    errors.append(error)
                else:
                    if not data[value]:
                        error = dict({ value: "Required" })
                        errors.append(error)
        return errors


class MealDate(BaseModel):
    __tablename__= 'mealdate'
    proposal_id = Column(Integer, ForeignKey('proposal.id'))
    user_id_1 = Column(Integer, ForeignKey('proposal.user_proposed_to'))
    user_id_2 = Column(Integer, ForeignKey('proposal.user_proposed_from'))
    restaurant_name = Column(String)
    restaurant_addres = Column(String)
    restaurant_picture = Column(String)

    @property
    def get_meal_time(self):
        p = session.query(Proposal).filter_by(id=self.proposal_id).first()
        p = session.query(DateTimeRequest).filter_by(id=p.request_id).first()
        # Crear funcion que retorne el formato adecuado @property
        return p.meal_time

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        "id" : self.id,
        "meal_time": self.meal_time,
        "restaurant_picture": self.restaurant_picture,
        "restaurant_address": self.restaurant_address,
        "restaurant_name": self.restaurant_name,
        "user_1": self.user_1,
        "user_2": self.user_2
        }

    @staticmethod
    def validate(data):
        errors = []
        required_fields = ['accept_proposal', 'proposal_id']
        if type(data) != dict:
            error = dict({"Missing required parameters":" ".format(', '.join(required_fields))})
            errors.append(error)
        else:
            for value in required_fields:
                if not value in data:
                    error = dict({ value: "Required" })
                    errors.append(error)
                else:
                    if not data[value]:
                        error = dict({ value: "Required" })
                        errors.append(error)
        return errors