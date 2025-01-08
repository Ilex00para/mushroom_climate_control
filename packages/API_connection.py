import requests
import re
import base64
import json
import datetime
from typing import List, Dict

class Timestamp:
    '''Class to generate the timestamp for API call'''
    def __init__(self, back_minutes=1):
        self.value = datetime.datetime.utcnow() - datetime.timedelta(minutes=back_minutes)
        self.timestamp = str(self.value.isoformat()).split('.')[0] + 'Z'

    def __str__(self):
        return self.value.isoformat(timespec='seconds') + 'Z'


class API_connection:
    """Class to interact with the API of 'The Things Network'. 
    Extraction of data from uplink messages of the last X minutes (can be adapted in the get_data method and is by default 1 min)."""

    def __init__(self, API_KEY, url='https://mcc.com/webhooks/datain') -> None:
        self.API_KEY = API_KEY
        self.url = url
        self.headers = {'Authorization' : f'Bearer {API_KEY}', 'Content-Type': 'text/event-stream', 'Accept': 'text/event-stream'}
        self.params = {"after": None} #by this the number of uplink messages is limited otherwise it will return all the uplink messages of the last 24h 

    def extract_data(self, measurement):
        try:
            ID_compartment = measurement['result']['end_device_ids']['device_id'][-1]
            measurement_time = datetime.datetime.fromisoformat(measurement['result']['received_at'].rstrip('Z'))
            avg_temperature, avg_relative_humidity, avg_co2 = base64.b64decode(measurement['result']['uplink_message']['frm_payload']).decode('utf-8').strip('( )').split(',')
            return {
                'ID_compartment': int(ID_compartment), 
                'measurement_time': measurement_time, 
                'avg_co2': round(float(avg_co2),2),
                'avg_temperature': round(float(avg_temperature),2), 
                'avg_relative_humidity': round(float(avg_relative_humidity),2)
                    }
        except KeyError as e:
            print(f"KeyError: Missing key in measurement: {e}")
        except Exception as e:
            print(e)
        return None

    def get_data(self, minutes_back=1) -> List[Dict]:

        self.params["after"] = str(Timestamp(minutes_back))
        
        r = requests.get(self.url+'uplink_message', headers=self.headers, params=self.params)
    
        # Check HTTP status before calling .json()
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch data from API.\nStatus Code: {r.status_code}\nURL: {r.url}\nResponse: {r.text}")
        else:
            try:
                measurements = re.findall(r'{.*}}}}',r.text) #looks for specific pattern in the things network
                for i, measurement in enumerate(measurements): 
                    measurements[i] = self.extract_data(json.loads(measurement)) #replaces the real values with processesed climate values
                return measurements
            except Exception as e:
                print(f"Error: {e}")
                return None

if __name__ == '__main__':
    API_KEY = "NNSXS.MLGVF5QOHIKWE6CM4CVTCINXIN5FYSYVBJWIRZQ.HGQBA3MLVVOX6XLWVQI26PSQX4TII5HT7NLP3YJZUIZTIDAEAMMA"
    api_connection = API_connection(API_KEY)
    climate_measurements = api_connection.get_data(minutes_back=10) 
    print(climate_measurements)