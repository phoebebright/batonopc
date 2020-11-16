from gascloud.gascloud import DataSource

from usbiss.spi import SPI
import opc

from datetime import datetime
import csv
import os
from os.path import basename
import json

# Open a SPI connection
spi = SPI("/dev/ttyACM0")

# Set the SPI mode and clock speed
spi.mode = 1
spi.max_speed_hz = 500000


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('./opcn3.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)



class OPCN3(DataSource):
    ''''''



    partic = None



    def __init__(self, settings_file=None, source_ref_file=None):
        super().__init__(settings_file, source_ref_file)

        self.connect2db()

        try:
            self.partic = opc.OPCN3(spi)
        except Exception as e:
            print("Startup Error: {}".format(e))

    def create_table_if_not_exists(self):
        '''this format is for testing - each source of data will have it's own format'''

        sql = f'''
               CREATE TABLE IF NOT EXISTS {self.db_table} (
               rdg_no integer PRIMARY KEY AUTOINCREMENT,
               timestamp text NOT NULL,
               gadget_id REAL,
               temp REAL,
               rh REAL,
               pm01 REAL,
               pm25 REAL,
               pm10 REAL,
               raw_data VARCHAR
               );
               '''
        self.db.execute(sql)

    def write_reading(self, gadget_id, **readings):

        timestamp = datetime.now()

        sql = f'''
               INSERT INTO {self.db_table} 
                 ('timestamp','gadget_id','temp','rh','pm01','pm25','pm10','raw_data')
               VALUES ('{timestamp:%Y-%m-%d %H:%M}',
                 '{gadget_id}', 
                 {readings['temp']},
                 {readings['rh']},
                 {readings['pm01']},
                 {readings['pm25']},
                 {readings['pm10']},
                 '{readings['raw_data']}')
               '''
        self.db.execute(sql)

    def wake(self):

        # Turn on the OPC
        self.partic.on()

    def sleep(self):

        # Turn off OPC
        self.partic.off()




    def round_dict(self, data, dp=1):
        '''round values in a dict - assumes all are numbers are round to same dp'''
        rounded = {}
        for k, v in data.items():
            try:
                rounded[k] = round(v, dp)
            except:
                rounded[k] = v

        return rounded



    def get_particulates(self):

        #TODO: generate error if n3 is not awake

        data = self.partic.histogram()

        # just pass back a subset for now
        readings = {}
        readings['temp'] = data['Temperature']
        readings['rh'] = data['Relative humidity']
        readings['pm01'] = data['PM_A']
        readings['pm25'] = data['PM_B']
        readings['pm10'] = data['PM_C']
        readings['raw_data'] = json.dumps(data)

        return self.round_dict(readings)


