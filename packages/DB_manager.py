import mysql.connector
from mysql.connector import errorcode
import logging
import time
from typing import List


class DB_manager():
    """Bot which interacts with the Database.
    
    Commands based on Code from MySQL Website https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html"""

    def __init__(self, config):
        self.config = config #cinfiguration dictionary
        

        self.logger = logging.getLogger(__name__)
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.handler = logging.StreamHandler()
        self.file_handler = logging.FileHandler("mushroom_climate_control/cpy-errors.log")
        self.logger.setLevel(logging.INFO)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        self.cnx = self.connect_to_mysql(self.config, attempts=3) #connection object
        
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

    def check_entry(self, table: str, features: List = None, condition: str =None) -> List[tuple]:
        '''Checks entries in the DB
        args:   
            table: str - name of the table in the DB
            features: List - list of features to be checked/retrieved
            condition: str - any condition to be met
        returns:
            query: list - list of tuples with the query results
        '''
        features = '*' if features is None else ', '.join(features)
        conditions = '' if condition is None else f'WHERE {condition}'
        command = f"SELECT {features} FROM {table} {conditions};"
        print(command)
        with self.cnx.cursor() as cursor:
            cursor.execute(command)
            query = cursor.fetchall()
        return query

    def writing_to_db(self, data: dict, verbose: bool = False) -> None:
        """Writes data to the DB using the self.add_climate_measurement command
        args:
            data: dict - dictionary with the data to be written
            verbose: bool - if True prints the data written
        """
        if self.cnx and self.cnx.is_connected():
            #creates the cursor to interact with the DB
            with self.cnx.cursor() as cursor:
                try:
                    cursor.execute(operation=self.add_climate_measurement,params=data)
                    if verbose:
                        print(f'Data were inserted into the Database.\n{data}')
                    self.cnx.commit()
                except mysql.connector.IntegrityError as err:
                    print("Error: {}".format(err))
                    query = self.check_entry('climate_compartments', ['ID_compartment'], f'ID_compartment = {data["ID_compartment"]}')
                    print(query)
        else:
            print('Not connected script closed.')