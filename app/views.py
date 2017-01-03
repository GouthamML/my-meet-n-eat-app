from models import *
from flask import Flask, jsonify, request, url_for, abort, g, redirect,render_template,flash,make_response
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, or_, and_
from datetime import datetime, time
from flask_httpauth import HTTPBasicAuth
from oauth import OAuthSignIn
from flask import session as login_session
from . import app

auth = HTTPBasicAuth()


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


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


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


@app.route('/')
@app.route('/index')
def index():
    if not login_session.get('username') :
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


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
    login_session['username'] = user.username
    token = user.generate_auth_token(1600)

    return redirect(url_for('index', token = token))

@app.route('/api/v1/logout', methods = ['GET'])
@auth.login_required
def logout():
    g.user = None
    return jsonify({"result": True})

