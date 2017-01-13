from models import *
from flask import g, flash
from . import login_manager
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

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
    r = datetime.date(year, month,day)
    return  r

#print parse_datetime(2000, 7, 2)