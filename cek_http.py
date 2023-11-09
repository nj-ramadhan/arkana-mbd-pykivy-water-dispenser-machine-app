import requests

try :
    r = requests.get('https://app.kickyourplast.com/api/products', {all : True})
    print(r.json()['data'][0])
except Exception as e:
    print(e)