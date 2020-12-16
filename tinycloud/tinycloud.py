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
from contextlib import closing

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# COPY OF CODE FROM gascloud_pi

SETTINGS = "settings.yaml"

VERSION = "1.3 Dec 2020"


class SettingsMixin():
    settings_file = "settings.yaml"
    settings = {}

    def __init__(self, settings=None, settings_file=None):
        '''pass either the settings as a dict or the settings_file '''

        if settings:
            self.settings = settings
        else:

            # assume settings file is in current directory
            if not settings_file:
                settings_file = self.settings_file

            self.settings = self.read_settings(settings_file)

    def read_settings(self, settings_file):

        # resolve relative path to full path
        settings_file = os.path.abspath(settings_file)

        if not os.path.exists(settings_file):
            raise ValueError(f"Settings file {settings_file} not found")

        with open(settings_file) as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)

        return settings


class ConnectDB(SettingsMixin):
    '''simple class to connect and retrieve readings from database'''

    settings_file = "settings.yaml"

    db_name = None
    db_table = None
    db_headings = []
    db = None
    connection = None

    def __init__(self, settings=None, settings_file=None):
        '''pass either the settings as a dict or the settings_file '''

        if settings:
            self.settings = settings
        else:

            # assume settings file is in current directory
            if not settings_file:
                settings_file = self.settings_file


            self.settings = self.read_settings(settings_file)


        self.connect2db()

    def read_settings(self, settings_file):

        # resolve relative path to full path
        settings_file = os.path.abspath(settings_file)

        if not os.path.exists(settings_file):
            raise ValueError(f"Settings file {settings_file} not found")

        with open(settings_file) as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)

        return settings

    def connect2db(self):

        self.db_name = os.path.abspath(self.settings['DBNAME'])
        self.db_table = self.settings['DB_TABLE']
        print(f"Connecting to {self.db_name}...")
        self.db = sqlite3.connect(self.db_name)
        self.db.row_factory = sqlite3.Row
        print(f"Connected to db {os.path.abspath(self.settings['DBNAME'])} using table {self.settings['DB_TABLE']}")

        # create database and table if doesn't exist
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        raise NotImplemented("Create function in class that generates data")


    def get_recent_readings(self, limit=10):

        sql = f"SELECT * FROM {self.db_table} ORDER BY rdg_no DESC LIMIT {limit}"

        result = self.db.execute(sql)

        return [dict(row) for row in result.fetchall()]

    def commit_sql(self, sql):

        c = self.db.cursor()

        # Execute SQL
        try:
            c.execute(sql)
            #print(f"SQL  : {sql}" )
        except sqlite3.Error as error:
            print(f"ERROR : DB FAILED to insert an entry : {error}")
        except Exception as e:
            print(f"EROR writing to DB: {e}")

        # then commit
        try:
            self.db.commit()
            # print("DB successfully commited a data entry insertion")

        except sqlite3.Error as error:
            print("ERROR : DB FAILED to commit a data entry insertion : ", error)


    def close_db(self):
        self.db.close()





class DataSource(ConnectDB):

    source_ref_file = "source_ref.csv"
    gateway_key_file = "gateway_key.txt"
    gadget_id = None



    def __init__(self, settings=None, settings_file=None, source_ref_file=None):
        '''

        :param settings_file: full path to device_settings.yaml if not using current path and/or default filename

        '''
        super().__init__(settings, settings_file)


        # TODO: handle missing gadget and might want to check this is a valid gadget in tinycloud
        self.gadget_id = self.settings['GADGET_ID']
        print(f"Data source gadget id {self.gadget_id}")



    def create_table_if_not_exists(self):
        '''this format is for testing - each source of data will have it's own format'''

        # want to know if table is created, so check first
        # get the count of tables with the name
        c = self.db.cursor()

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
        self.commit_sql(sql)



    def read_last(self, gadget_id):
        '''return a dictionary of the last reading or None if there is none'''
        sql = f"SELECT * FROM {self.db_table} WHERE gadget_id = '{gadget_id}' ORDER BY rdg_no DESC LIMIT 1"

        c = self.db.execute(sql)
        data = c.fetchone()
        if data:
            return dict(data)
        else:
            return None


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


class Batcher(SettingsMixin):
    '''handle interface and uploading of data to tinycloud from any device
    running python.  No UI'''



    gateway_key_file = "gateway_key.txt"
    batch_table = "Batches"
    gadget_id = None

    db_batch_name = None
    db_batch_table = None
    db_headings = []
    db_batch = None
    batch_connection = None


    def __init__(self, settings=None, settings_file=None):
        '''

        :param settings: pass in settings in a dict - see example_settings.yaml
        :param settings_file: full path to settings.yaml if not using default


        NOTE: a gateway key will be needed to upload to TheGasCloud - you can get a pin from thegascloud.com
        website, then run register.py, enter the pin when requested and new key will be retrieved from thegascloud.com.
        This steps requires internet access.
        '''

        super().__init__(settings, settings_file)

        # convert relative paths to abs paths
        self.settings['BATCH_DIR_PENDING'] = os.path.abspath(self.settings['BATCH_DIR_PENDING'])
        self.settings['BATCH_DIR_UPLOADED'] = os.path.abspath(self.settings['BATCH_DIR_UPLOADED'])

        # check the gateway key is available - this is the key for the device that is uploading,
        # not the device that is generating the data - although in this instance they are the same thing.

        self.gateway_key = self.get_gatewaykey()

        # keep a record of batches in an sqlite table
        self.connect2batchdb()
        self.create_batch_table_if_not_exists()


    def get_gatewaykey(self):
        key_file = os.path.abspath(self.gateway_key_file)
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

    def connect2batchdb(self):

        self.db_batch_name = os.path.abspath(self.settings['BATCH_DBNAME'])
        self.db_batch_table = self.settings['BATCH_TABLE']
        print(f"Connecting to {self.db_batch_name}...")

        self.db_batch = sqlite3.connect(self.db_batch_name)
        self.db_batch.row_factory = sqlite3.Row
        print(f"Connected to db {os.path.abspath(self.settings['BATCH_DBNAME'])} using table {self.settings['BATCH_TABLE']}")

        # create database and table if doesn't exist
        self.create_batch_table_if_not_exists()

    def create_batch_table_if_not_exists(self):
        '''this format is for testing - each source of data will have it's own format'''

        sql = f'''
              CREATE TABLE IF NOT EXISTS {self.batch_table} (
              source_id integer PRIMARY KEY AUTOINCREMENT,
              timestamp text NOT NULL,
              gadget_id REAL,
              reading_start REAL,
              reading_end REAL,
              batchid VARCHAR 
              );
              '''
        self.db.execute(sql)


    def get_reading_range(self, overlap=0):
        '''get range of readings to put in batch
        start with the last reading in the last batch and finish with the latest reading
         overlap allows for this many readings from the last batch to be included - useful when averaging'''
        #TODO: add  WHERE gadget_id = '{gadget_id}'

        first = None
        last = None

        # get last batch to find last reading sent
        sql = f"SELECT reading_end FROM {self.batch_table} ORDER BY reading_end DESC LIMIT 1"
        c = self.db_batch.execute(sql)
        data = c.fetchone()
        if data:
            first = dict(data)['reading_end']
        else:
            first = 0

        # get last reading to find max reading to send
        sql = f"SELECT * FROM {self.settings['DB_TABLE']} ORDER BY rdg_no DESC LIMIT 1"
        c = self.db.execute(sql)
        data = c.fetchone()
        if data:
            last = dict(data)['rdg_no']
        else:
            #TODO: handle empty
            last = None

        #TODO: need to lock this so only have one batch being sent at a time

        return first, last


    def make_batch(self):
        '''take data from readings datastore and create a batch from them and put in pending directory'''

        #TODO: check readings file exists and has more than 1 line


        if not os.path.exists(self.settings['BATCH_DIR_PENDING']):
            os.mkdir(self.settings['BATCH_DIR_PENDING'])


        # check the gateway key is available - this is the key for the device that is uploading,
        # not the device that is generating the data - although in this instance they are the same thing.

        gateway_key = self.get_gatewaykey()

        # get range of readings for this batch
        first, last = self.get_reading_range()

        # handle nothing to do
        if not last:
            print("Nothing to write")
            return

        batch = self.create_batch_record(first, last)


        source_ref = f"{batch['timestamp']}_{batch['source_id']}"
        fname = os.path.join(self.settings['BATCH_DIR_PENDING'],f"{source_ref}.csv")

        # create a csvfile of readings
        firstrow, lastrow = self.make_csvfile(fname, first, last)

        # name of yamlfile to go with it
        yamlfile = os.path.join(self.settings['BATCH_DIR_PENDING'], "%s.yaml" % source_ref)

        # names of files we are going to upload
        filelist = [fname,yamlfile]

        # create yamlfile with details of our batch
        self.make_yaml(yamlfile, self.settings['BATCH_TYPE'], self.settings['BATCH_MODE'], gateway_key, source_ref, batch['timestamp'],  filelist, gadget_id=self.gadget_id, range_written=[firstrow, lastrow])

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


        # now delete readings so don't get duplicates
        # delete readings now we have the zipfile

        # if self.settings['DELETE_READING_ON_ZIP']:
        #     logger.info("Deleting readings between %s and %s" % (range_written[0], range_written[1]))
        #     self.delete_readings_from_db(self.settings['DBNAME'], range_written[0], range_written[1])


        logger.info("Created batch %s" % source_ref)

        return fname

    def create_batch_record(self, first, last):

        timestamp = datetime.now()

        sql = f'''
              INSERT INTO {self.db_batch_table} 
                ('timestamp','gadget_id','reading_start','reading_end','batchid')
              VALUES ('{timestamp:%Y-%m-%d_%H:%M}',
                '{self.gadget_id}',
                {first},
                {last},
                'pending')
              '''

        c = self.db_batch.cursor()

        # Execute SQL
        try:
            c.execute(sql)
            # print(f"SQL  : {sql}" )
        except sqlite3.Error as error:
            print(f"ERROR : DB FAILED to insert an entry : {error}")
        except Exception as e:
            print(f"EROR writing to DB: {e}")

        # then commit
        try:
            self.db_batch.commit()
            # print("DB successfully commited a data entry insertion")

        except sqlite3.Error as error:
            print("ERROR : DB FAILED to commit a data entry insertion : ", error)

        if c.lastrowid:
            sql = f"SELECT * FROM  {self.db_batch_table} WHERE source_id =  {c.lastrowid}"
            result = self.db_batch.execute(sql)
            return dict(result.fetchone())

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

    def make_csvfile(self, fname, first, last):

        # get data to upload

        firstrow = None
        lastrow = None

        csvWriter = csv.writer(open(fname, "w+"))
        c = self.db.cursor()
        csvWriter.writerow(self.db_headings)


        for row in c.execute(f"SELECT * FROM {self.db_table}"):
            if not firstrow:
                firstrow = row[0]
            # use the cursor as an iterable
            csvWriter.writerow(row)
            lastrow = row[0]

        return firstrow, lastrow





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

        # if self.settings['GADGET_ID'] > ' ':
        #     gadget_id = self.settings['GADGET_ID']



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

        # if self.settings['GADGET_ID'] > ' ':
        #     payload['gadget_id'] = self.settings['GADGET_ID']

        headers = {f'Authorization': 'Bearer {self.gateway_key}'}

        response = requests.post(f"{self.settings['API']}/quarantine_request/" ,
                                 data=payload,
                                 headers=headers)

        if response.status_code == 200:
            creds = json.loads(response.content)
        else:
            raise ValueError(f"Quaratine request FAILED: {response.reason}")

        # add gateway key - this can be removed when tinycloud is updated to include this
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

