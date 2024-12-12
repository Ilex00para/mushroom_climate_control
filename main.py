from packages import API_connection, DB_manager
import datetime
import random

if __name__ == '__main__':

    config = {
        'user': 'bot',
        'password': 'mariadb2',
        'host': '127.0.0.1',
        'database': 'mushroom_cultivation',
        'raise_on_warnings': True
        }
    
    API_KEY = "NNSXS.MLGVF5QOHIKWE6CM4CVTCINXIN5FYSYVBJWIRZQ.HGQBA3MLVVOX6XLWVQI26PSQX4TII5HT7NLP3YJZUIZTIDAEAMMA"
    

    # mock_up_climate_data = {'ID_compartment': 1, 
    #                         'measurement_time': datetime.datetime.now(),
    #                         'avg_co2': random.uniform(400.0,3000.0),
    #                         'avg_temperature':random.uniform(0.0,30.0),
    #                         'avg_relative_humidity':random.uniform(0.0,100.0)
    #                         }

              
    api_connection = API_connection(API_KEY)
    db_manager = DB_manager(config)
    climate_measurements = api_connection.get_data()
    t = api_connection.params['after']
    for measurement in climate_measurements:
        db_manager.writing_to_db(measurement, verbose=True)
        
    


