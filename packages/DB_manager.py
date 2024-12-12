import mysql.connector
from mysql.connector import errorcode
import logging
import time


class DB_manager():
    """Bot which interacts with the Database.
    
    Commands based on Code from MySQL Website https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html"""

    def __init__(self, config):
        self.config = config #cinfiguration dictionary
        self.cnx = self.connect_to_mysql(self.config, attempts=3) #connection object

        self.logger = logging.getLogger(__name__)
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler = logging.StreamHandler()
        self.file_handler = logging.FileHandler("management_bot/cpy-errors.log")
        self.logger.setLevel(logging.INFO)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
        
        #Commands
        self.add_climate_measurement = "INSERT INTO climate_data \
                                        (ID_compartment, measurement_time, avg_co2, avg_temperature, avg_relative_humidity) \
                                        VALUES (%(ID_compartment)s, %(measurement_time)s, %(avg_co2)s, %(avg_temperature)s, %(avg_relative_humidity)s);"

    def connect_to_mysql(self, config: dict, attempts=3, delay=2):
        attempt = 1
        # Implement a reconnection routine
        while attempt < attempts + 1:      
            try:
                return mysql.connector.connect(**config)

            except (mysql.connector.Error, IOError)as err:
                if (attempts is attempt):
                    # Attempts to reconnect failed; returning None
                    self.logger.info("Failed to connect, exiting without a connection: %s", err)
                    return None
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)
                self.logger.info(
                    "Connection failed: %s. Retrying (%d/%d)...",
                    err,
                    attempt,
                    attempts-1,
                )
                # progressive reconnect delay
                time.sleep(delay ** attempt)
                attempt += 1

        return None 

    def check_last_entries(self):
        NotImplementedError           

    def writing_to_db(self, data: dict, verbose=False):
        if self.cnx and self.cnx.is_connected():
            #creates the cursor to interact with the DB
            with self.cnx.cursor() as cursor:
                
                cursor.execute(operation=self.add_climate_measurement,params=data)
                self.cnx.commit()
            if verbose:
                print(f'Data were inserted into the Database.\n{data}')
        else:
            print('Not connected script closed.')