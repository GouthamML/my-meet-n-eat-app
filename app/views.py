from models import *
from flask import jsonify, request, url_for, abort, g, redirect, render_template, flash, make_response
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, or_, and_
from datetime import datetime, time
from flask_httpauth import HTTPBasicAuth
from oauth import OAuthSignIn
from flask_login import login_required, login_user, logout_user, current_user
from flask import session as login_session
from utils import auth, verify_password, load_user, flash_errors, parse_datetime
from apis.foursquare_api import venues, get_country, getGeocodeLocation
from forms import LoginForm, RegisterForm, RequestForm
from . import app, login_manager, profile_photo

ip = 0

@app.before_request
def before_request():
    g.user = current_user
    global ip
    ip = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr


@app.route('/')
@app.route('/index')
def index():
    if not login_session.get('username') :
        return redirect(url_for('login'))
    return render_template('index.html',
                      user_authenticated=True,
                      login_session=login_session,
                      request=RequestForm(request.form))


@app.route('/login', methods=["GET", "POST"])
def login():
    #venues_query1 = venues(get_country(ip), mealtype='coffee')
    #venues_query2 = venues(get_country(ip))

    if login_session.get('username'):
        return redirect(url_for('index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        registered_user = session.query(User). \
                          filter_by(username=username).first()
        if registered_user is None or not registered_user.verify_password(password):
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('login'))
        image = session.query(ProfileImage).filter_by(user_id=registered_user.id).first()
        login_user(registered_user) #flask login
        login_session['username'] = registered_user.username
        login_session['picture'] = '../'+str(image.image_url)
        login_session['email'] = registered_user.email
        login_session['id'] = registered_user.id
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))

    return render_template('login.html',
                            user_authenticated=False,
                            formlogin=form,
                            formregister=RegisterForm(request.form)
                            )
#venues1=venues_query1,
#"venues2=venues_query2

@app.route('/register' , methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        user = User(username=form.username.data, email=form.email.data)
        query_validate_username = session.query(User).filter_by(username=form.username.data).first()
        query_validate_email = session.query(User).filter_by(email=form.email.data).first()
        if query_validate_username is not None or query_validate_email is not None:
            uri_parameters = 'invalid'
            flash('That dates in use')
            return redirect(url_for('login', error=uri_parameters))
        user.hash_password(form.password.data)
        session.add(user)
        session.commit()
        if 'profile_photo' in request.files:
            filename = profile_photo.save(request.files['profile_photo'])
            newprofilephoto = ProfileImage(user_id=user.id,
                                           image_filename=filename,
                                           image_url='static/img/profile/'+filename)
            session.add(newprofilephoto)
            session.commit()
        flash('User successfully registered')
    else:
        flash_errors(form)
        return redirect(url_for('login'))

    return redirect(url_for('login'))


@app.route('/logout', methods = ['GET'])
def logout():
    logout_user()
    g.user = None
    login_session.clear()
    return redirect(url_for('login')) 


@app.route('/oauth/<provider>')
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, picture = oauth.callback()
    user = session.query(User).filter_by(email=email).first()
    if not user:
        user = User(username = username, picture = picture, email = email)
        session.add(user)
        membership = OAuthMembership(provider = provider, provider_userid = social_id, user = user)
        session.add(membership)
        session.commit()
    login_user(user)
    login_session['username'] = user.username
    login_session['picture'] = picture # wtf
    login_session['email'] = user.email
    login_session['id'] = user.id
    token = user.generate_auth_token(1600)

    return redirect(url_for('index', token = token))


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/create_request', methods = ['GET', 'POST'])
def create_request():
    form = RequestForm(request.form)
    geolocation = getGeocodeLocation(form.location_string.data)
    if request.method == 'POST' and form.validate():
        newrequest = Request(user_id=login_session['id'],
                          meal_type=form.meal_type.data,
                          location_string=form.location_string.data,
                          latitude=geolocation[0],
                          longitude=geolocation[1])
        session.add(newrequest)
        session.commit()
        date_request = parse_datetime(year=form.year.data, month=form.month.data, day=form.day.data)
        if date_request == None:
            flash('Date no valid...')
            return redirect(url_for('index'))
        newrequestdate = DateTimeRequest(
                            request=newrequest.id,
                            mealtime=form.meal_time.data,
                            date=date_request)
        session.add(newrequestdate)
        session.commit()
        flash('Succefully!')
        return redirect(url_for('index'))
    flash_errors(form)
    return redirect(url_for('index'))


# Handling Error - - - - - - - - - - - - - - - - - - - - - - - 


@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)


@app.errorhandler(403)
def notauthorized(error):
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)

