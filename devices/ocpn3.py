from tinycloud.tinycloud import DataSource
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

        try:
            data = self.partic.histogram()
        except Exception as e:
            print("ERROR collecting data at {datetime.now()}. Skipping this reading")

        '''full data set
        {"Bin 0": 0.0,
         "Bin 1": 0.0,
         "Bin 2": 0.0,
         "Bin 3": 0.0,
         "Bin 4": 0.0,
         "Bin 5": 0.0,
         "Bin 6": 0.0,
         "Bin 7": 0.0,
         "Bin 8": 0.0,
         "Bin 9": 0.0,
         "Bin 10": 0.0,
         "Bin 11": 0.0,
         "Bin 12": 0.0,
         "Bin 13": 0.0,
         "Bin 14": 0.0,
         "Bin 15": 0.0,
         "Bin 16": 0.0,
         "Bin 17": 0.0,
         "Bin 18": 0.0,
         "Bin 19": 0.0,
         "Bin 20": 0.0,
         "Bin 21": 0.0,
         "Bin 22": 0.0,
         "Bin 23": 0.0,
         "Bin1 MToF": 0.0,
         "Bin3 MToF": 0.0,
         "Bin5 MToF": 0.0,
         "Bin7 MToF": 0.0,
         "Sampling Period": 169.18,
         "Sample Flow Rate": 3.69,
         "Temperature": 24.740978103303576,
         "Relative humidity": 42.20340276188296,
         "PM_A": 0.0,
         "PM_B": 0.0,
         "PM_C": 0.0,
         "Reject count Glitch": 0,
         "Reject count LongTOF": 0,
         "Reject count Ratio": 0,
         "Reject Count OutOfRange": 0,
         "Fan rev count": 0,
         "Laser status": 619,
         "Checksum": 36592}
'''
        readings = {}
        readings['temp'] = data['Temperature']
        readings['rh'] = data['Relative humidity']
        readings['pm01'] = data['PM_A']
        readings['pm25'] = data['PM_B']
        readings['pm10'] = data['PM_C']
        readings['raw_data'] = json.dumps(data)

        return self.round_dict(readings)

