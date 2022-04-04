import requests
headers={}
'''url = "http://mindfulrelax.ru/api/v1/auth/users/"
payload = {
    'email': 'alimama@gmd.com',
    'username': 'username@gmail.com',
    'password': 'password@ghyd.com'
}'''
url = "http://mindfulrelax.ru/api/v1/meditation/video/all/"
payload = {}
responseforattachement = requests.request("GET", url, headers=headers, data=payload).json()
len(responseforattachement)