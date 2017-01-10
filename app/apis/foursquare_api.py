import foursquare
import simplejson as json
import pycountry
from geoip import geolite2
import pycountry
from findARestaurant import foursquare_client_id, foursquare_client_secret
from geocode import getGeocodeLocation

# Construct the client object
client = foursquare.Foursquare(client_id='EXNP1PMGAF5XRDLQRXVTNUNG511YYDSBUFM2PEZXJEF0T0FY', client_secret='IGK5EP2XPEYFCQ0FZ0UFMZ5XBXI5DZ5RQ3EBH0IBXW15UENB', version='20130815')

def get_country(request_ip):
    math = geolite2.lookup(request_ip) if geolite2.lookup(request_ip) is not None else geolite2.lookup_mine()
    this_alpha = math.country
    tz = str(math.timezone)
    citycapital = tz[tz.index('/')+1:]
    for alpha in list(pycountry.countries):
        if this_alpha.__contains__(alpha.alpha2):
            this_alpha = alpha.name
    return str(this_alpha + ' , ' + citycapital)

countryvenues = get_country('127.0.0.1')

def venues(stringlocation, mealtype, limit=6):
    ll = getGeocodeLocation(stringlocation, None)
    ownvenue = client.venues.search(params={'limit': limit, 'll': ll, 'query': mealtype})
    p = ownvenue['venues']
    result = []
    for n in p:
        this = {}
        hours =  client.venues.hours(n['id'])
        hours = hours['hours']
        photo =  client.venues.photos(n['id'], params={'limit': 3})
        photo = photo['photos']
        this['name'] =  n['name']
        try : this['url'] = n['url']
        except: print 'No have url'
        try: this['location'] = n['location']['formattedAddress'][0]
        except: print 'No have location'
        try: this['menu_url'] = n['menu']['url']
        except: print 'No have Menu'
        try:
            for h in hours['timeframes']:
                this['days'] =  h['days']
                this['open'] =  h['open']
        except:
            print 'No Have Timeframes'

        try:
            for p in photo['items']:
                prefix = p['prefix']
                suffix = p['suffix']
                imageURL = prefix + "300x300" + suffix
                this['picture'] = imageURL
        except:
            print 'No have image'

        result.append(this)
    return result

json_venue = venues(countryvenues, 'pizza')

print json_venue