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
        readings['pm_01'] = data['PM_A']
        readings['pm_25'] = data['PM_B']
        readings['pm_10'] = data['PM_C']
        readings['bin_0'] = data['Bin 0']
        readings['bin_1'] = data['Bin 1']
        readings['bin_2'] = data['Bin 2']
        readings['bin_3'] = data['Bin 3']
        readings['bin_4'] = data['Bin 4']
        readings['bin_5'] = data['Bin 5']
        readings['bin_6'] = data['Bin 6']
        readings['bin_7'] = data['Bin 7']
        readings['bin_8'] = data['Bin 8']
        readings['bin_9'] = data['Bin 9']
        readings['bin_10'] = data['Bin 10']
        readings['bin_11'] = data['Bin 11']
        readings['bin_12'] = data['Bin 12']
        readings['bin_13'] = data['Bin 13']
        readings['bin_14'] = data['Bin 14']
        readings['bin_15'] = data['Bin 15']
        readings['bin_16'] = data['Bin 16']
        readings['bin_17'] = data['Bin 17']
        readings['bin_18'] = data['Bin 18']
        readings['bin_19'] = data['Bin 19']
        readings['bin_20'] = data['Bin 20']
        readings['bin_21'] = data['Bin 21']
        readings['bin_22'] = data['Bin 22']
        readings['bin_23'] = data['Bin 23']

        readings['bin1_mtof'] = data['Bin1 MToF']
        readings['bin3_mtof'] = data['Bin3 MToF']
        readings['bin5_mtof'] = data['Bin5 MToF']
        readings['bin7_mtof'] = data['Bin7 MToF']

        readings['sampling_period'] = data['Sampling Period']
        readings['sample_flow_rate'] = data['Sample Flow Rate']

        readings['reject_count_glitch'] = data['Reject count Glitch']
        readings['reject_count_longtof'] = data['Reject count LongTOF']
        readings['reject_count_ratio'] = data['Reject count Ratio']
        readings['reject_count_outofrange'] = data['Reject Count OutOfRange']
        readings['fan_rev_count'] = data['Fan rev count']
        readings['last_status'] = data['Laser status']
        readings['checksum'] = data['Checksum']

        return self.round_dict(readings)

