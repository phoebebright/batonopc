from gascloud.gascloud import GasCloudInterface as GasCloudMixin

from usbiss.spi import SPI
import opc

from datetime import datetime
import csv
import os
from os.path import basename

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



class OPCN3(GasCloudMixin):
    ''''''

    readings_file = None
    readings_file_path = None

    partic = None



    def __init__(self, settings_file=None, source_ref_file=None):
        super().__init__(settings_file, source_ref_file)

        self.readings_file = "readings.csv"

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

    def set_readings_file_path(self):

        self.readings_file_path = os.path.join(self.cwd, self.readings_file)

    def create_readings_file(self):
        if not self.readings_file_path:
            self.set_readings_file_path()

        if not os.path.exists(self.readings_file_path):
            with open(self.readings_file_path, "w") as file:
                writer = csv.writer(file)
                writer.writerow(["rtype", "seconds", "value1","value2","value3"])
                writer.writerow([0, datetime.utcnow().isoformat(),"","",""])

        return self.readings_file_path

    def delete_readings_file(self):

        if os.path.exists(self.readings_file_path):
            os.remove(self.readings_file_path)
            self.readings_file_path = None

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
        readings['temperature'] = data['Temperature']
        readings['rh'] = data['Relative humidity']
        readings['pm01'] = data['PM_A']
        readings['pm25'] = data['PM_B']
        readings['pm10'] = data['PM_C']

        return self.round_dict(readings)


    def write_reading(self, reading, csvwriter):
        '''called at log_interval to write current readings to database'''

        csvwriter.writerow(reading)

    def make_batch(self):
            '''take data from readings.csv and create a batch from them the clear down readings.csv'''

            #TODO: check readings file exists and has more than 1 line


            if not os.path.exists(self.settings['BATCH_DIR_PENDING']):
                os.mkdir(self.settings['BATCH_DIR_PENDING'])


            if self.settings['GADGET_ID'] > ' ':
                gadget_id = self.settings['GADGET_ID']

            # check the device key is available - this is the key for the device that is uploading,
            # not the device that is generating the data - although in this instance they are the same thing.
            device_key = self.get_devicekey()


            # create filename with date and load data from sqlite db
            when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_write = self.get_last_source_ref()
            next_sequence = int(last_write['sequence'])+1
            source_ref = "%s_%0.6d_%s" % (device_key, next_sequence, datetime.utcnow().strftime("%Y%m%d%H%M%S"))



            fname = os.path.join(self.settings['BATCH_DIR_PENDING'],"%s.csv" % source_ref)

            #TODO: work without having to stop logging

            # move current readings file to pending directory and assuming method logging data will create a new readings file
            os.rename(self.readings_file_path, fname)

            #TODO: put something useful in range_written
            range_written = [0,1]
            # if no data, then nothing to do - might want to make a setting so downloads anyway
            # if not range_written[0]:
            #     print("No data to download")
            #     return

            # name of yamlfile to go with it
            yamlfile = os.path.join(self.settings['BATCH_DIR_PENDING'], "%s.yaml" % source_ref)

            # names of files we are going to upload
            filelist = [fname,yamlfile]

            # create yamlfile with details of our batch
            self.make_yaml(yamlfile, self.settings['BATCH_TYPE'], self.settings['BATCH_MODE'], device_key, source_ref, when,  filelist, gadget_id=gadget_id, range_written=range_written)

            # create zipfile but use the source_ref, it will be renamed when we have a batchid
            tempzipname = os.path.join( self.settings['BATCH_DIR_PENDING'], "%s.zip" % source_ref)

            zip_size, zip_md5 = self.make_zipfile(tempzipname, filelist)

            # make yaml file with details of batch
            payload = {
                'key': device_key,
                'source_ref': source_ref,
                'filelist': "%s,%s" % (basename(filelist[0]), basename(filelist[1])),
                'batch_type': self.settings['BATCH_TYPE'],
                'batch_mode': self.settings['BATCH_MODE'],
                'zip_size': zip_size,
                'zip_md5': zip_md5,

            }
            payload_yaml_name = os.path.join(self.settings['BATCH_DIR_PENDING'], "%s.yaml" % source_ref)
            self.make_payload_yaml(payload_yaml_name, payload)

            self.put_next_source_ref(next_sequence, source_ref, zip_size, zip_md5, datetime.utcnow().isoformat())

            # now delete readings so don't get duplicates
            # delete readings now we have the zipfile

            if self.settings['DELETE_READING_ON_ZIP']:
                logger.info("Deleting readings between %s and %s" % (range_written[0], range_written[1]))
                self.delete_readings_from_db(self.settings['DBNAME'], range_written[0], range_written[1])


            logger.info("Created batch %s" % source_ref)




    def create_table_if_not_exists(self):
        #NOT CURRENTLY USED
        sql = f'''
            CREATE TABLE IF NOT EXISTS {self.db_table} (
            rdg_no integer PRIMARY KEY AUTOINCREMENT,
            timestamp text NOT NULL,
            temp REAL,
            rh REAL
            );
            '''
        self.db.execute(sql)