from models import *
from flask import Flask, jsonify, request, url_for, abort, g, redirect,render_template,flash, make_response
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, or_, and_
from datetime import datetime, time
from flask_httpauth import HTTPBasicAuth
from oauth import OAuthSignIn
from flask_login import login_required, login_user, logout_user, current_user
from flask import session as login_session
from utils import auth, verify_password, load_user, flash_errors
from forms import LoginForm, RegisterForm
from . import app, login_manager, profile_photo

ip = 0

@app.before_request
def before_request():
    print remote_addr
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
                      login_session=login_session)


@app.route('/login', methods=["GET", "POST"])
def login():
    if login_session.get('username') :
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
                            formregister=RegisterForm(request.form))

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


#  API - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@app.route('/api/v1/logout', methods = ['GET'])
@auth.login_required
def logout_api():
    g.user = None
    login_session = None
    return jsonify({"result": True})

@app.route('/api/v1/login', methods = ['POST'])
def api_login():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        print "missing arguments"
        abort(400)
    username = request.json.get('username')
    password = request.json.get('password')
    user = session.query(User).filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return jsonify({"result": False})
    token = user.generate_auth_token(6000)
    return jsonify({'token': token.decode('ascii')})

@app.route('/api/v1/users', methods= ['GET'])
@auth.login_required
def get_users():
    users = session.query(User).all()
    return jsonify(users = [u.serialize for u in users])

@app.route('/api/v1/users', methods= ['POST'])
def new_user():
    if not request.json or not 'username' in request.json or not 'password' in request.json:
        print "missing arguments"
        abort(400)
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        abort(400)
    if session.query(User).filter_by(username = username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 409#, {'Location': url_for('get_user', id = user.id, _external = True)}

    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    token = user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

@app.route('/api/v1/users/token/<token>/id/<int:id>', methods=['PUT'])
@auth.login_required
def update_user(token, id):
    user = session.query(User).filter_by(id=id).first()
    if user is None:
        abort(400)
    elif user.verify_auth_token(token) is not None:
        user.generate_auth_token()
    else:
        return jsonify({'message':'token no valid'}), 409
    return jsonify({'token': token.decode('ascii')})

@app.route('/api/v1/users/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    user = session.query(User).filter_by(id = id).first()
    if user is None:
        abort(404)
    return jsonify(user.serialize)

@app.route('/api/v1/requests', methods=['GET'])
@auth.login_required
def get_requests():
    user = g.user
    requests = session.query(Request).filter(user.id != Request.user_id).all()
    return jsonify(requests = [r.serialize for r in requests])

@app.route('/api/v1/requests/me', methods=['GET'])
@auth.login_required
def get_my_requests():
    user = g.user
    requests = session.query(Request).filter(user.id == Request.user_id).all()
    return jsonify(requests = [r.serialize for r in requests])

@app.route('/api/v1/requests', methods=['POST'])
@auth.login_required
def new_request():
    user = g.user
    if not request.json:
        abort(400)
    errors = Request.validate(request.json)
    if len(errors) == 0:
        meal_type = request.json.get('meal_type')
        longitude = request.json.get('longitude')
        latitude = request.json.get('latitude')
        location_string = request.json.get('location_string')
        meal_time = request.json.get('meal_time')
        r = Request(user_id = user.id,meal_type = meal_type, longitude = longitude, latitude = latitude, location_string = location_string, meal_time = meal_time)
        session.add(r)
        session.commit()
        return  jsonify( { 'result': True } ),201
    return jsonify({"message": "The request is invalid."},errors = [error for error in errors])  ,400

@app.route('/api/v1/requests/<int:id>', methods=['GET'])
@auth.login_required
def get_request(id):
    r = session.query(Request).filter_by(id = id).first()
    if r is None:
        abort(404)
    return jsonify(r.serialize)

@app.route('/api/v1/requests/<int:id>', methods=['PUT'])
@auth.login_required
def update_request(id):
    user = g.user
    if not request.json:
        abort(400)
    errors = Request.validate(request.json)
    if len(errors) == 0:
        return  jsonify( { 'result': True } )

    return jsonify({"message": "The request is invalid."},errors = [error for error in errors])  ,400

@app.route('/api/v1/requests/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_request(id):
    user = g.user
    r = session.query(Request).filter_by(id = id).first()
    if r is None:
        abort(404)
    if user.id != r.user_id:
        abort(403)
    session.delete(r)
    session.commit()
    return  jsonify( { 'result': True } )

@app.route('/api/v1/proposals', methods=['GET'])
@auth.login_required
def get_proposals():
    user = g.user
    proposals = session.query(Proposal).filter(Proposal.user_proposed_to == user.id).all()
    return jsonify(proposals = [proposal.serialize for proposal in proposals])

@app.route('/api/v1/proposals/me', methods=['GET'])
@auth.login_required
def get_my_proposals():
    user = g.user
    proposals = session.query(Proposal).filter(Proposal.user_proposed_from == user.id).all()
    return jsonify(proposals = [proposal.serialize for proposal in proposals])

@app.route('/api/v1/proposals', methods=['POST'])
@auth.login_required
def new_proposal():
    user = g.user
    if not request.json:
        abort(400)
    errors = Proposal.validate(request.json)
    if len(errors) == 0:
        request_id = request.json.get('request_id')
        r = session.query(Request).filter_by(id = request_id).first()
        if r is None:
            return jsonify({"message": "The request is invalid."},errors = [dict({"request_id":"Request does not exist"})])  ,400
        if user.id == r.user_id:
            abort(403)
        proposal = Proposal(user_proposed_from = user.id, user_proposed_to = r.user_id, request_id = r.id  )
        session.add(proposal)
        session.commit()
        return  jsonify( { 'result': True } )
    return jsonify({"message": "The request is invalid."},errors = [error for error in errors])  ,400

@app.route('/api/v1/proposals/<int:id>', methods=['GET'])
@auth.login_required
def get_proposal(id):
    user = g.user
    proposal = session.query(Proposal).filter_by(id = id).first()
    if proposal is None:
        abort(404)
    if proposal.user_proposed_to != user.id and proposal.user_proposed_from != user.id:
        abort(403)
    return jsonify(proposal.serialize)

@app.route('/api/v1/proposals/<int:id>', methods=['PUT'])
@auth.login_required
def update_proposal(id):
    user = g.user
    if not request.json:
        abort(400)
    errors = Proposal.validate(request.json)
    if len(errors) == 0:
        return  jsonify( { 'result': True } )
    return jsonify({"message": "The request is invalid."},errors = [error for error in errors])  ,400

@app.route('/api/v1/proposals/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_proposal(id):
    proposal = session.query(Proposal).filter_by(id = id).first()
    if proposal is None:
        abort(404)
    if proposal.user_proposed_from != user.id:
        abort(403)
    session.delete(proposal)
    session.commit()
    return  jsonify( { 'result': True } )

@app.route('/api/v1/dates', methods=['GET'])
@auth.login_required
def get_dates():
    user = g.user
    dates = session.query(MealDate).filter(or_(MealDate.user_1 == user.id, MealDate.user_2 == user.id)).all()
    return jsonify(dates = [date.serialize for date in dates])


@app.route('/api/v1/dates', methods=['POST'])
@auth.login_required
def new_date():
    user = g.user
    if not request.json:
        abort(400)
    errors = MealDate.validate(request.json)
    if len(errors) == 0:
        proposalsa_id = request.json.get('proposal_id')
        accept_proposal = request.json.get('accept_proposal')
        proposal = session.query(Proposal).filter_by(id = proposal_id).first()
        if proposal is None:
            abort(404)
        r = proposal.request
        if r.filled:
            return  jsonify( { 'result': False } )
        if accept_proposal:
            proposal.filled = True
            r.filled = True
            restaurant_picture = "No Restaurants Found"
            restaurant_address = "No Restaurants Found"
            restaurant_name =  "No Restaurants Found"
            try:
                result = findARestaurant(r.meal_type, r.location_string)
                if type(result) == dict:
                    restaurant_picture = result.get('name')
                    restaurant_address = result.get('address')
                    restaurant_name =  result.get('image')
            except Exception as e:
                 print e
            date = MealDate(meal_time = r.meal_time, user_1 = r.user_id , user_2 = proposal.user_proposed_from, restaurant_picture = restaurant_picture,restaurant_address = restaurant_address, restaurant_name= restaurant_name )
            session.add(date)
            session.add(proposal)
            session.add(r)
            session.commit()
            return  jsonify( { 'result': True } )
        else:
            session.delete(proposal)
            session.commit()
            return  jsonify( { 'result': True } )

    return jsonify({"message": "The request is invalid."},errors = [error for error in errors])  ,400

@app.route('/api/v1/dates/<int:id>', methods=['GET'])
@auth.login_required
def get_date(id):
    user = g.user
    date = session.query(MealDate).filter_by(id = id).first()
    if date is None:
        abort(404)
    if date.user_1 != user.id and date.user_2 != user.id:
        abort(403)
    return jsonify(date.serialize)

@app.route('/api/v1/dates/<int:id>', methods=['PUT'])
@auth.login_required
def update_date(id):
    user = g.user
    if not request.json:
        abort(400)
    date = session.query(MealDate).filter_by(id = id).first()
    if data is None:
        abort(404)
    errors = MealDate.validate(request.json)
    if len(errors) == 0:
        return  jsonify( { 'result': True } )

    return jsonify({"message": "The request is invalid."},errors = [error for error in errors])  ,400



@app.route('/api/v1/dates/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_date(id):
    date = session.query(MealDate).filter_by(id = id).first()
    if date is None:
        abort(404)
    if date.user_1 != user.id and date.user_2 != user.id:
        abort(403)
    session.delete(date)
    session.commit()
    return  jsonify( { 'result': True } )