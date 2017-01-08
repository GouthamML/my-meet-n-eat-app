from findARestaurant import foursquare_client_id, foursquare_client_secret
from geocode import getGeocodeLocation, google_api_key
import foursquare

# Construct the client object
client = foursquare.Foursquare(client_id='EXNP1PMGAF5XRDLQRXVTNUNG511YYDSBUFM2PEZXJEF0T0FY', client_secret='IGK5EP2XPEYFCQ0FZ0UFMZ5XBXI5DZ5RQ3EBH0IBXW15UENB', version='20130815')

ownvenue = client.venues.search(params={'ll': u'40.7,-74.0', 'query': 'coffee'})

p = ownvenue['venues']
for n in p:
    print n[u'name']