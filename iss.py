import requests
import json
from datetime import datetime

def get_iss_location():
    endpoint = 'http://api.open-notify.org/iss-now.json'
    response = requests.get(endpoint)
    response_json = response.json()
    # long_lat = response_json['iss_position']
    
    return(response_json)

    # Return in json format {"iss_position": {"latitude": "-49.4665", "longitude": "-51.0737"}, "message": "success", "timestamp": 1552249236}

# print(get_iss_location())

def get_iss_pass_time(latitude, longitude):
    endpoint = 'http://api.open-notify.org/iss-pass.json'
    coords = {'lat': latitude, 'lon': longitude}

    response = requests.get(endpoint, params = coords)
    # print('response json {}'.format(response.json()))

    date_list = response.json().get('response')
    pass_time_unix = int(date_list[0].get('risetime'))

    return(datetime.utcfromtimestamp(pass_time_unix).strftime('%Y-%m-%d %H:%M:%S'))

# print(get_iss_pass_time('-52.0', '10.0'))

            
    # Return in following format 2019-03-10 23:56:31
def get_iss_pass_time_from_postcode(postcode):
    endpoint = 'http://api.postcodes.io/postcodes/{}'.format(postcode)    
    response = requests.get(endpoint).json()
    
    lat = response.get('result').get('latitude')
    lon = response.get('result').get('longitude')
    
    return(get_iss_pass_time(lat, lon)) 

print(get_iss_pass_time_from_postcode('e145gl'))

