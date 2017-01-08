from wtforms import *
from wtforms.fields.html5 import EmailField, DateTimeField
from . import profile_photo
from flask_wtf.file import FileField, FileAllowed, FileRequired


class SuperForm(Form):
    submit = SubmitField('Submit')


class RegisterForm(Form):
    username = StringField('Username',   [
        validators.Regexp('^\w+$', message="Regex: Username must contain only letters numbers or underscore"),
        validators.DataRequired(message='El campo esta vacio.'),
        validators.length(min=5, message='Min 5 letter, Try Again')])

    password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm_password', message='Passwords must match'),
        validators.Regexp('[A-Za-z0-9@#$%^&+=]{8,}', message="Regex: At least 8 letter"),
        validators.DataRequired(message='El campo esta vacio.'),
        validators.length(min=8, message='Min 8 letter, Try Again')])

    confirm_password = PasswordField('Repeat Password')

    email = EmailField('Email', [
        validators.Required(),
        validators.EqualTo('confirm_email', message='Email must match'),
        validators.Regexp('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', message="Regex: Incorrect format"),
        validators.Email('Ingrese un email valido'), validators.DataRequired(message='El campo esta vacio.'),
        validators.length(min=7, message='Min:5, letter, Try Again')])

    confirm_email = EmailField('Repeat Email')

    profile_photo = FileField('', validators=[FileRequired(), FileAllowed(profile_photo, 'Images only!')])


class LoginForm(SuperForm):
    username = StringField('',   [validators.DataRequired(message='El campo esta vacio.'), validators.length(min=5, message='Min 5 letter, Try Again')])
    password = PasswordField('', [validators.DataRequired(message='El campo esta vacio.'), validators.length(min=8, message='Min 8 letter, Try Again')])



class Request(SuperForm):
    meal_type = StringField('',   [validators.DataRequired(message='El campo esta vacio.'), validators.length(min=3, message='Min 5 letter, Try Again')])
    location_string = PasswordField('', [validators.DataRequired(message='El campo esta vacio.')])
    meal_time = DateTimeField('Time', [validators.DataRequired(message='El campo esta vacio.')])
