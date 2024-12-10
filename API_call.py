import requests
import base64
import json
import datetime

type = 'uplink_message'
API_KEY = "NNSXS.MLGVF5QOHIKWE6CM4CVTCINXIN5FYSYVBJWIRZQ.HGQBA3MLVVOX6XLWVQI26PSQX4TII5HT7NLP3YJZUIZTIDAEAMMA"
url = f'https://eu1.cloud.thethings.network/api/v3/as/applications/first-application-one/packages/storage/{type}'
headers =   {'Authorization' : f'Bearer {API_KEY}', 'Content-Type': 'text/event-stream', 'Accept': 'text/event-stream'}

class Timestamp:
    '''Class to generate the timestamp for API call'''
    def __init__(self, back_minutes=1):
        self.value = datetime.datetime.utcnow() - datetime.timedelta(minutes=back_minutes)
        self.timestamp = str(self.value.isoformat()).split('.')[0] + 'Z'

    def __str__(self):
        return self.timestamp

#only messages after 5 minutes ago !!! can be adapted to any time
params = {"after": str(Timestamp(1)), "limit": 1}

r = requests.get(url, headers=headers, params=params)

# Check HTTP status before calling .json()
if r.status_code != 200:
    raise RuntimeError(f"The status code is not 200. \nSTATUS CODE: {r.status_code} \nTEXT: {r.text}")
else:
    try:
        # Parse the response JSON
        response_data = r.json()

        # Extract the payload
        if 'result' in response_data and 'uplink_message' in response_data['result']:
            payload = base64.b64decode(response_data['result']['uplink_message']['frm_payload'])
            print(payload)
        else:
            print("No uplink_message or result found in the response.")
    
    except KeyError as e:
        print(f"KeyError: Missing key in response: {e}")
    
    except Exception as e:
        # Handle any other exceptions
        if 'error' in response_data:
            print(f"\nAn error has occurred: {response_data['error']['message']}")
        else:
            raise RuntimeError("An unexpected problem occurred") from e