import requests
api_key = 'AIzaSyDnT-MA1Zhi9Y85n2ukMW61YKfKXFpoyDY'

import requests
import json

#api_key = 'YOUR_API_KEY'
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=new+york+city+point+of+interest&language=en&key=' + api_key

response = requests.get(url)
data = json.loads(response.text)
print(data.keys())

for result in data['results']:
    print(result['name'])
    print('Rating:', result['rating'])

