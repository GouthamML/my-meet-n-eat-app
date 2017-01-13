from wtforms import *
from wtforms.fields.html5 import EmailField
from wtforms_components import TimeField
import datetime
import calendar
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



class RequestForm(SuperForm):
    a = list(range(1, 32))
    c = map(str, list(range(1, len(calendar.month_name))))

    meal_type = StringField('Example: Coffee or Donuts',   [validators.DataRequired(message='El campo esta vacio.'), validators.length(min=3, message='Min 5 letter, Try Again')])
    location_string = StringField('Location', [validators.DataRequired(message='El campo esta vacio.')])
    meal_time = SelectField('year', choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('afternoon snack', 'Afternoon snack'), ('dinner', 'Dinner')])
    year = SelectField('year', choices=[('2017', '2017'), ('2018', '2018')])
    month = SelectField('month', choices=zip(c, list(calendar.month_name)[1:]))
    day = SelectField('day', choices=zip(map(str, a), a))
