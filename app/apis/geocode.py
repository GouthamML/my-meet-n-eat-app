import httplib2
import simplejson as json

try:
    google_api_key = json.loads(
        open('google_maps.json', 'r').read())['geocoding']['key']
except IOError:
    google_api_key = "AIzaSyB0sqYi14-q7hMIHeZluGLCGZKxIETxIHY"


def getGeocodeLocation(inputString, context='findARestaurant'):
    # Use Google Maps to convert a location into Latitute/Longitute coordinates
    # FORMAT: https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY
    locationString = inputString.replace(" ", "+")
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'% (locationString, google_api_key))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    if context == 'findARestaurant':
        return (latitude, longitude)
    else:
        return str(latitude) + ',' + str(longitude)

