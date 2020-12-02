import requests
import os
import json
import paramiko
from scp import SCPClient
import time
from zipfile import ZipFile
import sqlite3
from datetime import datetime
import csv
import yaml
from os.path import basename
import logging
import hashlib
from time import gmtime, strftime
from pathlib import Path

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# COPY OF CODE FROM gascloud_pi

SETTINGS = "settings.yaml"

VERSION = "1.3 Dec 2020"


class ConnectDB():
    '''simple class to connect and retrieve readings from database'''

    settings_file = "settings.yaml"

    db_name = None
    db_table = None
    db_headings = []
    db = None
    connection = None

    def __init__(self, settings_file=None):

        # assume settings file is in current directory
        if not settings_file:
            settings_file = self.settings_file

        self.settings = self.read_settings(settings_file)

        self.connect2db()

    def read_settings(self, settings_file):

        # assume if starts "/" then it is a full path, otherwise put current directory in front of it
        # there is surely a safer way of doing this!
        if not settings_file[0] == "/":

            settings_file = os.path.join(Path.cwd(), settings_file)

        if not os.path.exists(settings_file):
            raise ValueError(f"Settings file {settings_file} not found")

        with open(settings_file) as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)

        return settings

    def connect2db(self):
        self.db_name = self.settings['DBNAME']
        self.db_table = self.settings['DB_TABLE']

        self.db = sqlite3.connect(self.db_name)
        self.db.row_factory = sqlite3.Row

        # create database and table if doesn't exist
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
         raise NotImplemented("Create function in class that generates data")


    def delete_readings_from_db(self, from_reading, to_reading):
        # get data to upload


        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()

            try:
                c.execute(f'DELETE FROM {self.db_name} WHERE DataID BETWEEN {from_reading} AND {to_reading}')
            except sqlite3.Error as e:
                print("Database error: %s" % e)
            except Exception as e:
                print("Exception in _query: %s" % e)

    def get_recent_readings(self):

            sql = f"SELECT * FROM {self.db_table} ORDER BY timestamp DESC LIMIT 10"

            result = self.db.execute(sql)

            return result.fetchall()

class DataSource(ConnectDB):

    source_ref_file = "source_ref.csv"

    gadget_id = None



    def __init__(self, settings_file=None, source_ref_file=None):
        '''

        :param settings_file: full path to device_settings.yaml if not using current path and/or default filename

        '''
        super().__init__(settings_file)


        # TODO: handle missing gadget and might want to check this is a valid gadget in gascloud
        self.gadget_id = self.settings['GADGET_ID']


        # get full path of source_ref and make sure we have one, creating if necessary
        if source_ref_file:
            self.source_ref_file = source_ref_file
        self.get_or_create_source_ref_file()

    def create_table_if_not_exists(self):
        '''this format is for testing - each source of data will have it's own format'''

        sql = f'''
              CREATE TABLE IF NOT EXISTS {self.db_table} (
              rdg_no integer PRIMARY KEY AUTOINCREMENT,
              timestamp text NOT NULL,
              gadget_id REAL,
              temp REAL,
              rh REAL,
              raw_data VARCHAR
              );
              '''
        self.db.execute(sql)

    def write_reading(self, gadget_id, **readings):

        timestamp = datetime.now()

        sql = f'''
              INSERT INTO {self.db_table} 
                ('timestamp','gadget_id','temp','rh','raw_data')
              VALUES ('{timestamp:%Y-%m-%d %H:%M}',
                '{gadget_id}', 
                {readings['temp']},
                {readings['rh']},
                '{readings['raw_data']}')
              '''
        self.db.execute(sql)


    def read_last(self, gadget_id):

        sql = f"SELECT * FROM {self.db_table} WHERE gadget_id = '{gadget_id}' ORDER BY timestamp DESC LIMIT 1"

        result = self.db.execute(sql)

        rowDict = dict(zip([c[0] for c in result.description], result.fetchone()))

        return rowDict

    def close_db(self):

        self.db.close()




    def get_devicekey(self):
        key_file = os.path.join(Path.cwd, self.gateway_key_file)
        try:
            f = open(key_file)
            self.gateway_key = f.read()
        except:
            print('Gateway Key cannot be found')
            return None

        if len(self.gateway_key) != 20:
            print("Invalid Gateway key")
            return None

        return self.gateway_key


    def get_or_create_source_ref_file(self):
        '''convert filename to path and check file exists'''

        # assume if starts "/" then it is a full path, otherwise put current directory in front of it
        # there is surely a safer way of doing this!
        if not self.source_ref_file[0] == "/":
            self.source_ref_file = os.path.join(Path.cwd(), self.source_ref_file)

        if not os.path.exists(self.source_ref_file):
            with open(self.source_ref_file, "w") as file:
                csvwriter = csv.DictWriter(file, fieldnames=["sequence", "timestamp", "source_ref"])
                csvwriter.writeheader()
                csvwriter.writerow({'sequence': 0, 'timestamp': datetime.utcnow().isoformat(), 'source_ref': ""})


    def get_or_create_readings_file(self):
        '''create readings csv file if doesn't already exist and return path to readings file'''

        if not self.readings_file_path:
            self.set_readings_file_path()

        if not os.path.exists(self.readings_file_path):
            with open(self.readings_file_path, "w") as file:
                writer = csv.writer(file)
                writer.writerow(["rtype", "seconds", "value1", "value2", "value3"])
                writer.writerow([0, datetime.utcnow().isoformat(), "", "", ""])

        return self.readings_file_path

    def delete_readings_file(self):

        if os.path.exists(self.readings_file_path):
            os.remove(self.readings_file_path)
            self.readings_file_path = None




    def make_batch(self):
            '''take data from readings datastore and create a batch from them and put in pending directory'''

            #TODO: check readings file exists and has more than 1 line


            if not os.path.exists(self.settings['BATCH_DIR_PENDING']):
                os.mkdir(self.settings['BATCH_DIR_PENDING'])


            if self.settings['GADGET_ID'] > ' ':
                gadget_id = self.settings['GADGET_ID']

            # check the gateway key is available - this is the key for the device that is uploading,
            # not the device that is generating the data - although in this instance they are the same thing.
            #TODO: rename as gateway_key
            gateway_key = self.get_devicekey()


            # create filename with date and load data from sqlite db
            when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_write = self.get_last_source_ref()
            next_sequence = int(last_write['sequence'])+1
            source_ref = "%s_%0.6d_%s" % (gateway_key, next_sequence, datetime.utcnow().strftime("%Y%m%d%H%M%S"))



            fname = os.path.join(self.settings['BATCH_DIR_PENDING'],"%s.csv" % source_ref)

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
            self.make_yaml(yamlfile, self.settings['BATCH_TYPE'], self.settings['BATCH_MODE'], gateway_key, source_ref, when,  filelist, gadget_id=gadget_id, range_written=range_written)

            # create zipfile but use the source_ref, it will be renamed when we have a batchid
            tempzipname = os.path.join( self.settings['BATCH_DIR_PENDING'], "%s.zip" % source_ref)

            zip_size, zip_md5 = self.make_zipfile(tempzipname, filelist)

            # make yaml file with details of batch
            payload = {
                'key': gateway_key,
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

            return gateway_key




class GasCloudInterface(ConnectDB):
    '''handle interface and uploading of data to gascloud from any device
    running python.  No UI'''


    settings_file = "settings.yaml"
    gateway_key_file = "gateway_key.txt"

    data_sources = []



    def __init__(self, settings_file=None, source_ref_file=None):
        '''

        :param settings_file: full path to settings.yaml if not using default
        :param source_ref_file: full path to source_ref.csv if not using default

        NOTE: a gateway key will be needed to upload to TheGasCloud - you can get a pin from thegascloud.com
        website, then run register.py, enter the pin when requested and new key will be retrieved from thegascloud.com.
        This steps requires internet access.
        '''

        super().__init__(settings_file=None)





        # check the gateway key is available - this is the key for the device that is uploading,
        # not the device that is generating the data - although in this instance they are the same thing.

        self.gateway_key = self.get_gatewaykey()


        # self.db_name = self.settings['DBNAME']
        # self.db_table = self.settings['DB_TABLE']
        # # create database and table if doesn't exist
        # self.db = sqlite3.connect(self.db_name)

        # self.create_table_if_not_exists()


    def get_gatewaykey(self):
        key_file = os.path.join(Path.cwd, self.gateway_key_file)
        try:
            f = open(key_file)
            self.gateway_key = f.read()
        except:
            print('Gateway Key cannot be found')
            return None

        if len(self.gateway_key) != 20:
            print("Invalid Gateway Key")
            return None

        return self.gateway_key

    def make_yaml(self, yamlfile, batch_type, batch_mode, device_id, source_ref, when, filelist, gadget_id, range_written):

        # TODO: add GPS location when available

        content = {
            'source': 'Raspberry PI',
            'source_ref': source_ref,
            'version': VERSION,
            'filelist': filelist,
            'batch_type': batch_type,
            'batch_mode': batch_mode,
            'device_id': device_id,
            'timestamp': when,
            'gadget_id': gadget_id,
            'reading_from': range_written[0],
            'reading_to': range_written[1],
        }

        # create yaml file

        with open(yamlfile, 'w') as file:
            documents = yaml.dump(content, file)

    def make_payload_yaml(self, yamlfile, content):

        # create yaml file

        with open(yamlfile, 'w') as file:
            documents = yaml.dump(content, file)


    def make_zipfile(self,zipfname, filelist):
        '''put files in filelist into a zip and return size (in kb) and md4'''

        m = hashlib.md5()
        with ZipFile(zipfname, 'w') as zipObj:
            for f in filelist:
                zipObj.write(f, basename(f))
                #m.update(f)

                # # delete once added to zip - if we get a fail before finishing, the data will still be in the database
                # os.remove(f) # hmm may not want to do this here

        return os.path.getsize(zipfname), m.hexdigest()

    def make_csvfile(self, fname):

        lastrow = None
        firstrow = None

        # get data to upload
        with sqlite3.connect(self.db_name) as connection:

            csvWriter = csv.writer(open(fname, "w+"))
            c = connection.cursor()
            csvWriter.writerow(self.db_headings)


            for row in c.execute(f"SELECT * FROM {self.db_table}"):
                if not firstrow:
                    firstrow = row[0]
                # use the cursor as an iterable
                csvWriter.writerow(row)
                lastrow = row[0]

        return firstrow, lastrow



    def get_last_source_ref(self):
        '''get next number in sequence and return between optional prefix and suffix'''

        with open(self.source_ref_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            # to reduce memory usage (presumably) read each line to end of file to get last line
            # rather than loading everything into memory
            for row in reader:
                lastrow = row

        return lastrow

    def put_next_source_ref(self,*args):
        '''get next number in sequence and return between optional prefix and suffix'''

        with open(self.source_ref_file, 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(args)

    def upload_all(self):
        ''' attempt to upload all files in the pending directory '''



        if not os.path.exists(self.settings['BATCH_DIR_PENDING']):
            os.mkdir(self.settings['BATCH_DIR_PENDING'])
            return "Nothing to do"

        if not os.path.exists(self.settings['BATCH_DIR_UPLOADED']):
            os.mkdir(self.settings['BATCH_DIR_UPLOADED'])

        if self.settings['GADGET_ID'] > ' ':
            gadget_id = self.settings['GADGET_ID']



        batches_uploaded = []
        for folderName, subfolders, filenames in os.walk(self.settings['BATCH_DIR_PENDING']):
            for filename in filenames:
                parts = filename.split(".")

                # if called with a datatype, match that to the first part of the filename
                if parts[-1] == "zip":
                    zipfile = os.path.join(folderName, filename)

                    # There may be batches that were successfully uploaded but did not get an update status in time
                    # We don't want to upload them again, so just add them to the list of files to do a status check on
                    if len(filename) == 36:
                        batchid = filename[:32]
                        batches_uploaded.append(batchid)

                    else:
                        # try uploading this these zip files (still named with source_ref)

                        batchid = self.upload(zipfile)
                        batches_uploaded.append(batchid)


        # check to see if it has arrived - try every 5 seconds for 1 minute
        # there must be a nicer way of doing this!
        for n in range(1, 20):
            time.sleep(5)

            # keep checking batches
            if len(batches_uploaded) < 1:
                break

            headers = {'Authorization': 'Bearer ' + self.gateway_key}

            for batch in batches_uploaded:
                print("Checking status of batch %s" % batch)

                url = "%s/upload_status/%s/" % (self.settings['API'], batch)
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    status = json.loads(response.content)
                    if status['status'] == "Rejected":
                        print("Batch rejected by quarantine server")
                    elif status['status'] == "Unprocessed":
                        print("Batch successfully uploaded and pending processing")
                        self.batch_uploaded( batch)
                        batches_uploaded.remove(batch)
                    elif status['status'] == "Processed":
                        print("Batch successfully uploaded and processed")
                        self.batch_uploaded( batch)
                        batches_uploaded.remove(batch)
                    else:
                        print(status['status'])

                else:
                    print("Unable to get status")
                    return

    def upload(self, zipfile):
        '''try uploading a zipfile'''

        # look for yaml file with same name as zip - this will have payload for making quarantine request
        payload_file = "%s.yaml" % zipfile[:-4]
        if not os.path.exists(payload_file):
            raise ValueError("Unable to upload %s as missing matching yaml payload file" % zipfile)

        with open(payload_file) as file:
            payload = yaml.load(file, Loader=yaml.FullLoader)

        # make quarantine request

        if self.settings['GADGET_ID'] > ' ':
            payload['gadget_id'] = self.settings['GADGET_ID']

        headers = {f'Authorization': 'Bearer {self.gateway_key}'}

        response = requests.post(f"{self.settings['API']}/quarantine_request/" ,
                                 data=payload,
                                 headers=headers)

        if response.status_code == 200:
            creds = json.loads(response.content)
        else:
            raise ValueError(f"Quaratine request FAILED: {response.reason}")

        # add gateway key - this can be removed when gascloud is updated to include this
        creds['destination'] += f"{self.gateway_key}/inbox/"

        # rename zipfile and payload yaml with batchid now we have it (we will have to name back again if upload fails)
        zipfname = os.path.join(os.path.dirname(os.path.realpath(zipfile)), "%s.zip" % (creds["batchid"]))
        os.rename(zipfile, zipfname)
        new_payload_file = os.path.join(os.path.dirname(os.path.realpath(payload_file)), "%s.yaml" % (creds["batchid"]))
        os.rename(payload_file, new_payload_file)

        try:
            self.upload_zip(zipfname, creds)
        except Exception as e:
            # rename back again so we can retry
            os.rename(zipfname, zipfile)
            os.rename(new_payload_file, payload_file)
            raise

        print("Uploaded files %s to quarantine server %s to  %s" % (
            payload['filelist'], creds['domain'], creds['destination']))

        return creds['batchid']



    def upload_zip(self, zipfile, creds):

        # attempt scp
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(creds['domain'],
                    port=int(creds['port']),
                    username=self.gateway_key,
                    password=creds['batchid'],
                    )

        with SCPClient(ssh.get_transport()) as scp:
            try:
                scp.put(zipfile, creds['destination'], preserve_times=True)
            except Exception as e:
                print("Error in scp to quarantine: %s" % e)
                raise

    def batch_uploaded(self, batchid):

        # move to uploaded dir or delete
        zipname = os.path.join(self.settings['BATCH_DIR_PENDING'], batchid + ".zip")
        payload_file = os.path.join(self.settings['BATCH_DIR_PENDING'], batchid + ".yaml")

        if self.settings['DELETE_BATCH_ON_UPLOAD']:
            os.remove(zipname)
            os.remove(payload_file)
        else:
            newname = os.path.join(self.settings['BATCH_DIR_UPLOADED'], basename(zipname))
            os.rename(zipname, newname)

            newname = newname.replace('.zip', '.yaml')
            os.rename(payload_file, newname)

