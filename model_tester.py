from app.models import *
from colorama import init as init_color, Fore as color
from apis.findARestaurant import findARestaurant as restaurant
from apis.geocode import getGeocodeLocation as geolocation
from datetime import datetime
import simplejson as json
import pycountry
import time


# Init colorama module for awesome print :)

init_color()

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()


usernames = [('charlyjazz', 'password1', 'email1@gmail.com'),
            ('kathorq', 'password2', 'email2@gmail.com'),
            ('willy_chessy', 'password3', 'email3@gmail.com'),
            ('god_good', 'password4', 'email4@gmail.com')]

query_mealtype = ['donuts', 'pizza', 'burguer', 'coffee', 'seafood']

def add_user():
    for data in usernames:
        if session.query(User).filter_by(username = data[0]).first() is None:
            print(color.CYAN + data[0])
            user = User(username = data[0])
            user.hash_password(data[1])
            user.set_email(data[2])
            session.add(user)
            session.commit()
    return True


def assert_user():
    count_id = len(usernames) - len(usernames) + 1
    for data in usernames:
        user = session.query(User).filter_by(username=data[0]).first()
        print(color.LIGHTCYAN_EX + '---------------')
        print user.id, count_id
        print(color.BLUE + user.username)
        print(str(user.verify_password(data[1])))
        print(user.email)
        assert user.id == count_id, 'No math id'
        count_id += 1
    return True


def create_request():
    countries = []
    for country in pycountry.countries:
        countries.append(country.name)
    country = random.choice(countries)
    #willy_chessy got a request
    user = session.query(User).filter_by(username=usernames[2][0]).first()
    request = Request(user_id=user.id,
         meal_type=random.choice(query_mealtype),
         location_string=country,
         latitude=geolocation(country)[0],
         longitude=geolocation(country)[1],
         meal_time=datetime.now(),
         filled=False)
    session.add(request)
    session.commit()
    return True


def all_requests():
    all_request = session.query(Request).all()
    for i in all_request:
        print(color.LIGHTCYAN_EX + '---------------')
        print(color.BLUE + str(i.id))
        print(i.user_id)
        print(i.meal_type)
        print(i.location_string)
        print(i.latitude)
        print(i.longitude)
        print(i.meal_time)
        print(i.filled)
    return True


def create_proposal(meal_type='coffee'):
    request = session.query(Request).filter_by(meal_type=meal_type).first()
    id_user_proposed_to = session.query(User.id).filter_by(username=usernames[0][0]).first()
    #proposed to charlyjazz from willy_chessy
    if request is not None:
        proposal = Proposal(
            user_proposed_to=id_user_proposed_to[0],
            user_proposed_from=request.user_id,
            request_id=request.id,
            filled=True)
        session.add(proposal)
        session.commit()
    return True

def create_mealdate(id=1):
    # Users confirm proposal:
    proposal = session.query(Proposal).filter_by(id=id).first()
    request = (proposal.get_request_data)

    rest = restaurant(request['meal_type'], request['location'])
    print(color.MAGENTA + unicode(rest['name']))
    print(unicode(rest['address']))
    print(str(rest['image']))
    
    #creating mealdate!
    mealdate = MealDate(
        proposal_id=proposal.id,
        user_id_1=proposal.user_proposed_to,
        user_id_2=proposal.user_proposed_from,
        restaurant_name = unicode(rest['name']),
        restaurant_addres = unicode(rest['address']),
        restaurant_picture = rest['image']
    )

    session.add(mealdate)
    session.commit()
    return True

def assert_mealdate():
    # willy_chessy mealdate
    user = session.query(User).filter_by(username=usernames[2][0]).first()
    mealdate = session.query(MealDate).filter_by(user_id_2=user.id).first()
    print mealdate.get_meal_time

if __name__ == '__main__':
    print(color.LIGHTGREEN_EX + 'TEST FOR MODELS OF MEET AND MEAN').center(85)
    #time.sleep(2)
    #add_user()
    #assert_user()
    #create_request()
    #all_requests()
    #create_proposal()
    #create_mealdate()
    #assert_mealdate()