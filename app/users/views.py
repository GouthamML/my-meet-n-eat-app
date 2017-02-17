from ..models import *
from flask import jsonify, request, url_for, g, redirect, render_template, flash, make_response, Blueprint
import simplejson as json
from oauth import OAuthSignIn
from flask_login import login_user, current_user
from flask import session as login_session
from utils import auth, flash_errors, parse_datetime, login_required
from apis.foursquare_api import venues, getGeocodeLocation
from forms import LoginForm, RegisterForm, RequestForm, SearchForm
from .. import profile_photo, csrf

ip = 0
searchform = SearchForm

mod = Blueprint('users', __name__, template_folder='templates')

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

@mod.before_request
def before_request():
    g.user = current_user
    global ip
    ip = request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") else request.remote_addr


@mod.route('/')
@mod.route('/index')
def index():
    if not login_session.get('username') :
        return redirect(url_for('users.login'))

    request_user = session.query(Request, DateTimeRequest). \
    filter(Request.user_id==login_session['id']). \
    filter(DateTimeRequest.request==Request.id).all()

    return render_template('index.html',
                      user_authenticated=True,
                      login_session=login_session,
                      request=RequestForm(request.form),
                      request_user=request_user,
                      searchform=searchform(request.form))


@mod.route('/login', methods=["GET", "POST"])
def login():
    if login_session.get('username'):
        return redirect(url_for('users.index'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        registered_user = session.query(User). \
                          filter_by(username=username).first()
        if registered_user is None or not registered_user.verify_password(password):
            flash('Username or Password is invalid' , 'error')
            return redirect(url_for('users.login'))
        image = session.query(ProfileImage).filter_by(user_id=registered_user.id).first()
        login_user(registered_user) #flask login
        login_session['username'] = registered_user.username
        login_session['picture'] = '../'+str(image.image_url)
        login_session['email'] = registered_user.email
        login_session['id'] = registered_user.id
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('users.index'))

    return render_template('login.html',
                            user_authenticated=False,
                            formlogin=form,
                            formregister=RegisterForm(request.form),
                            searchform=searchform(request.form),
                            )

@mod.route('/register' , methods=['GET','POST'])
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
        print request.files
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
        return redirect(url_for('users.login'))

    return redirect(url_for('users.login'))


@mod.route('/logout', methods = ['GET'])
def logout():
    # this need refactor
    login_session.clear()
    return redirect(url_for('users.login'))


@mod.route('/oauth/<provider>')
def oauth_authorize(provider):
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@mod.route('/callback/<provider>')
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

    return redirect(url_for('users.index', token = token))


@mod.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@mod.route('/create_request', methods = ['GET', 'POST'])
def create_request():
    form = RequestForm(request.form)
    if request.method == 'POST' and form.validate():
        geolocation = getGeocodeLocation(form.location_string.data)
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
            return redirect(url_for('users.index'))
        newrequestdate = DateTimeRequest(
                            request=newrequest.id,
                            mealtime=form.meal_time.data,
                            date=date_request)
        session.add(newrequestdate)
        session.commit()
        flash('Succefully!')
        return redirect(url_for('users.index'))
    flash_errors(form)
    return redirect(url_for('users.index'))

@mod.route('/request/delete/<int:id>', methods=['GET', 'POST'])
def delete_request(id):
    user = g.user
    r = session.query(Request).filter_by(id = id).first()
    d = session.query(DateTimeRequest).filter_by(request = r.id).first()
    session.delete(r)
    session.delete(d)
    session.commit()
    return redirect(url_for('users.index'))

@mod.route('/request/edit', methods=['POST'])
def request_edit():
    if request.method == "POST":
        data = json.loads(request.data)
        request_query = session.query(Request).filter_by(id = data['id']).first()
        request_query_datetime = session.query(DateTimeRequest).filter_by(request = request_query.id).first()

        geolocation = getGeocodeLocation(data['location'])

        new = [data['meal_type'], data['location'],
               geolocation[0], geolocation[1]]
        old = [request_query.meal_type, request_query.location_string,
               request_query.latitude, request_query.longitude]

        if set(new) != set(old):
            request_query.edit_meal_type = data['meal_type']
            request_query.edit_location_string = data['location']
            request_query.edit_latitude = geolocation[0]
            request_query.edit_longitude = geolocation[1]
            session.add(request_query)
            session.commit()

    return redirect(url_for('users.index'))

@mod.route('/request/edit/values', methods=['GET', 'POST'])
def values_form_edit_request():
        if request.method == "GET":
            request_id = request.args.get('id')
            print request_id
            r = session.query(Request).filter_by(id = request_id).first()
            #print r.serialize
            return json.dumps({'status':'OK',
                                'meal': r.serialize
                              })


@csrf.exempt
@mod.route('/search/', methods=['POST'])
def search():
    form = searchform(request.form)
    if form.validate():
        city = form.search.data
        venues_query = venues(city, mealtype='donuts', limit=5)
        return render_template('explorer.html',
                               query=venues_query,
                               searchform=searchform(request.form))


@mod.route('/request/all', methods=['GET'])
def all_request():
    form = searchform(request.form)
    requests = session.query(Request, DateTimeRequest). \
    filter(Request.filled==False).all()
    return render_template('all_request.html',
                           requests=requests,
                           searchform=searchform(request.form))


@mod.route('/proposal/create/<int:id>', methods=['GET'])
def create_proposal(id):
    r = session.query(Request).filter_by(id=id).first()
    if  r.user_id == login_session['id']:
        flash('Cannot create proposal for your request')
        return redirect(url_for('users.all_request'))
    p = Proposal(
        user_proposed_to=login_session['id'],
        user_proposed_from=r.user_id,
        request_id=r.id,
        filled=False
    )
    session.add(p)
    session.commit()
    flash('Succefully!')
    return redirect(url_for('users.index'))

@mod.route('/proposal/me', methods=['GET'])
@login_required
def my_proposal():
    form = searchform(request.form)
    proposal_me = session.query(Proposal).filter_by(
                user_proposed_to=login_session['id']
                ).all()
    proposal_from = session.query(Proposal).filter_by(
                user_proposed_from=login_session['id']
                ).all()
    return render_template('proposal/proposal_all.html',
                           proposal_me=proposal_me,
                           proposal_from=proposal_from,
                           searchform=searchform(request.form))

@mod.route('/proposal/confirm/<int:id>', methods=['GET'])
def confirm_proposal(id):
    p = session.query(Proposal).filter_by(id=id).first()
    #: Hay inconsistencias con los venues. A veces vienen incompletos
    #: Se necesita hacer una busqueda mas inteligente y capturar excepciones
    #: Hasta poder dar un resultado sea cula sea, mas cercano al practico
    if(p is not None):
        rest = venues('Caracas',
                      'Coffee',
                      limit=1)
        print rest
        mealdate = MealDate(
            proposal_id=p.id,
            user_id_1=p.user_proposed_to,
            user_id_2=p.user_proposed_from,
            restaurant_name=unicode(rest[0]['name']),
            restaurant_addres=rest[0]['location'],
            restaurant_picture=rest[0]['picture']
        )
        session.add(mealdate)
        session.commit()
        flash('Meal created!')
        return redirect(url_for('users.my_mealdate'))
    flash('Error') # BUG
    return redirect(url_for('users.index'))


@mod.route('/mealdate/me', methods=['GET'])
@login_required
def my_mealdate():
    form = searchform(request.form)
    m = session.query(MealDate).filter_by(user_id_2=login_session['id']).all()
    if m == None:
        flash('You not have Mealdates')
        return redirect(url_for('users.index'))
    return render_template('mealdate/mealdate_all.html',
                           mealdate_all=m,
                           searchform=searchform(request.form))