import requests
import json


# RAPID API CLIMACELL
def climaCell_Temperature():
    lat = 11.4218
    lon = 76.8617
    url = "https://climacell-microweather-v1.p.rapidapi.com/weather/realtime"
    querystring = {"unit_system": "si",
                   "fields": ["temp"], "lat": lat, 'lon': lon}
    headers = {
        'x-rapidapi-host': 'climacell-microweather-v1.p.rapidapi.com',
        'x-rapidapi-key': '331beb605emshe23730cae5866ecp1695fdjsn3506622aa61a'
    }
    response = requests.request('GET', url, headers=headers, params=querystring).json()

    return response['temp']['value']
