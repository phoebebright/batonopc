import os
import sys

# get the full path to the folder one level above where the current file
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

from tinycloud.tinycloud import DataSource # batonopc
from .opcn3_batcher import OPCN3_SaveMixin

from usbiss.spi import SPI
import opc

from datetime import datetime
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
    '''Class to manage collection of data from the OPC and writing of data to database'''


    partic = None


    def __init__(self, settings=None, settings_file=None, source_ref_file=None):
        super().__init__(settings, settings_file, source_ref_file)

        self.connect2db()

        # self.gateway_key = self.get_gatewaykey()

        try:
            self.partic = opc.OPCN3(spi)
        except Exception as e:
            print("Startup Error: {}".format(e))

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

