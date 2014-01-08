import urllib
import urllib2
import simplejson as json

class GeocoderServiceError(Exception):
    pass

def _build_url(params):
    GOOGLE_GEOCODE_BASE_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
    return GOOGLE_GEOCODE_BASE_URL + '?' + urllib.urlencode(params)

def _get_url_data(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.URLError, e:
        raise GeocoderServiceError('URLError: %s' % e.reason)

def _check_result_is_valid(result):
    if result is None:
        raise GeocoderServiceError('Geocoding service unavailable')
    elif not result.has_key('status'):
        raise GeocoderServiceError('Geocoding result parse error')
    elif result['status'] != 'OK':
        raise GeocoderServiceError('Geocoding status error: %s'
                % result['status'])
    elif not result.has_key('results'):
        raise GeocoderServiceError('Geocoding result parse error')
    elif len(result['results']) == 0:
        raise GeocoderServiceError('No geocoding results')

def _unpack_geocode_data(result):
    _check_result_is_valid(result)

    fresult = result['results'][0]
    if not fresult.has_key('geometry'):
        raise GeocoderServiceError('Geocoding result parse error')
    elif not fresult['geometry'].has_key('location'):
        raise GeocoderServiceError('Geocoding result parse error')
    else:
        lresult = fresult['geometry']['location']
        if not (lresult.has_key('lat') and lresult.has_key('lng')):
            raise GeocoderServiceError('Geocoding result parse error')
        else:
            ne = fresult['geometry']['viewport']['northeast']
            sw = fresult['geometry']['viewport']['southwest']
            return {
                'location': {
                    'lat': lresult['lat'],
                    'lon': lresult['lng'],
                },
                'boundingbox': {
                    'top': ne['lat'],
                    'bottom': sw['lat'],
                    'left': sw['lng'],
                    'right': ne['lng'],
                },
            }


def _unpack_reverse_geocode_data(result):
    _check_result_is_valid(result)

    fresult = result['results'][0]

    if not fresult.has_key('formatted_address'):
        raise GeocoderServiceError('Geocoding result parse error')
    if not fresult.has_key('address_components'):
        raise GeocoderServiceError('Geocoding result parse error')
    for comp in fresult['address_components']:
        if not comp.has_key('long_name') or not comp.has_key('types'):
            raise GeocoderServiceError('Geocoding result parse error')

    full_address = fresult['formatted_address']
    countries = [comp['long_name']
                 for comp in fresult['address_components']
                 if 'country' in comp['types']]

    if len(countries) == 0:
        raise GeocoderServiceError('Geocoding result parse error')

    return full_address, countries[0]


def geocode(address):
    """
    Geocode a given address using the Google API. Returns a tuple of
    (lat, lon) float values.

    >>> geocode("Kongens Nytorv 6, 1050 Copenhagen K, Denmark")
    (55.68114360, 12.58664570)
    """
    params = [('address', address), ('sensor', 'false')]
    url = _build_url(params)
    page = _get_url_data(url)
    result = json.load(page)
    location = _unpack_geocode_data(result)['location']
    return location['lat'], location['lon']

def geocode2(address):
    """
    Geocode a given address using the Google API. Returns a dictionary
    with "location" and "boundingbox":

    >>> from pprint import pprint
    >>> pprint(geocode("Kongens Nytorv 6, 1050 Copenhagen K, Denmark"))
    {'boundingbox': {'bottom': 55.6797946197085,
                     'left': 12.5852967197085,
                     'right': 12.5879946802915,
                     'top': 55.6824925802915},
     'location': {'lat': 55.6811436, 'lon': 12.5866457}}
    """
    params = [('address', address), ('sensor', 'false')]
    url = _build_url(params)
    page = _get_url_data(url)
    result = json.load(page)
    return _unpack_geocode_data(result)

def reverse_geocode(lat, lng):
    params = [('latlng', str(lat) + ',' + str(lng)), ('sensor', 'false')]
    url = _build_url(params)
    page = _get_url_data(url)
    result = json.load(page)
    return _unpack_reverse_geocode_data(result)
