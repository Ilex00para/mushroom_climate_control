import requests
import base64
import json
import datetime


API_KEY = "NNSXS.MLGVF5QOHIKWE6CM4CVTCINXIN5FYSYVBJWIRZQ.HGQBA3MLVVOX6XLWVQI26PSQX4TII5HT7NLP3YJZUIZTIDAEAMMA"
url = 'https://eu1.cloud.thethings.network/api/v3/as/applications/first-application-one/packages/storage/'
headers =   {'Authorization' : f'Bearer {API_KEY}', 'Content-Type': 'text/event-stream', 'Accept': 'text/event-stream'}

class Timestamp:
    '''Class to generate timestamp for API call'''
    def __init__(self, back_minutes=1):
        self.value = datetime.datetime.now() - datetime.timedelta(minutes=back_minutes)
        self.timestamp = f'{str(self.value).split(' ')[0]}T{str(self.value).split(' ')[1].split('.')[0]}Z'

        

params = {'limit': 1}
r = requests.get(url, headers=headers, params=params)
r = r.json()
payload = base64.b64decode(r['result']['uplink_message']['frm_payload'])
print(type(payload))
