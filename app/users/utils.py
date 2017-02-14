from flask import g, flash, redirect, url_for, request
from views import login_session
from flask_httpauth import HTTPBasicAuth
from functools import wraps
from ..models import *

from .. import login_manager

auth = HTTPBasicAuth()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'username' in login_session:
            return redirect(url_for('users.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(id):
    return session.query(User).get(int(id))

@auth.verify_password
def verify_password(username_or_token, password):
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

def parse_datetime(year, month, day):
    import datetime
    year = int(year); month = int(month); day = int(day)
    if datetime.date(year, month,day) > datetime.date.today():
        result = datetime.date(year, month, day)
    else:
        result = None
    return result

#print parse_datetime(2000, 7, 2)