import requests
import re
import base64
import json
import datetime

class Timestamp:
    '''Class to generate the timestamp for API call'''
    def __init__(self, back_minutes=1):
        self.value = datetime.datetime.utcnow() - datetime.timedelta(minutes=back_minutes)
        self.timestamp = str(self.value.isoformat()).split('.')[0] + 'Z'

    def __str__(self):
        return self.value.isoformat(timespec='seconds') + 'Z'


class API_connection:
    """Class to interact with the API of 'The Things Network'. 
    Extraction of data from uplink messages of the last 'minutes_back' minutes."""
    def __init__(self, API_KEY, url='https://eu1.cloud.thethings.network/api/v3/as/applications/first-application-one/packages/storage/'):
        self.API_KEY = API_KEY
        self.url = url
        self.headers = {'Authorization' : f'Bearer {API_KEY}', 'Content-Type': 'text/event-stream', 'Accept': 'text/event-stream'}
        self.params = {"after": None} #by this the number of uplink messages is limited otherwise it will return all the uplink messages of the last 24h 

    def extract_data(self, measurement):
        try:
            ID_compartment = measurement['result']['end_device_ids']['device_id'][-1]
            measurement_time = datetime.datetime.fromisoformat(measurement['result']['received_at'].rstrip('Z'))
            avg_temperature, avg_relative_humidity, avg_co2 = base64.b64decode(measurement['result']['uplink_message']['frm_payload']).decode('utf-8').strip('( )').split(',')
            return {'ID_compartment': int(ID_compartment), 
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

    def get_data(self, minutes_back=1):

        self.params["after"] = str(Timestamp(minutes_back))
        
        r = requests.get(self.url+'uplink_message', headers=self.headers, params=self.params)
    
        # Check HTTP status before calling .json()
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch data from API.\nStatus Code: {r.status_code}\nURL: {r.url}\nResponse: {r.text}")
        else:
            try:
                measurements = re.findall(r'{.*}}}}',r.text)
                for i, measurement in enumerate(measurements):
                    measurements[i] = self.extract_data(json.loads(measurement))
                return measurements
            except Exception as e:
                print(f"Error: {e}")
                return None