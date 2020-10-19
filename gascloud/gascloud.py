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

# COPY OF CODE FROM gascloud_pi

SETTINGS = "settings.yaml"

VERSION = "1.1 Sep 2020"



class GasCloudInterface():
    '''handle interface and uploading of data to gascloud from any device
    running python.  No UI'''

    db_name = None
    db_table = None
    db_headings = []
    db = None
    settings_file = "settings.yaml"
    device_key_file = "device_key.txt"
    source_ref_file = "source_ref.csv"
    cwd = None




    def __init__(self, settings_file=None, source_ref_file=None):
        '''

        :param settings_file: full path to settings.yaml if not using default
        :param source_ref_file: full path to source_ref.csv if not using default
        '''

        self.cwd = Path.cwd()

        # assume settings file is in current directory
        if not settings_file:
            settings_file = self.settings_file

        self.settings = self.read_settings(settings_file)

        # get full path of source_ref and make sure we have one, creating if necessary
        if source_ref_file:
            self.source_ref_file = source_ref_file
        self.get_or_create_source_ref_file()

        # check the device key is available - this is the key for the device that is uploading,
        # not the device that is generating the data - although in this instance they are the same thing.

        self.device_key = self.get_devicekey()


    def get_or_create_source_ref_file(self):
        '''convert filename to path and check file exists'''

        # assume if starts "/" then it is a full path, otherwise put current directory in front of it
        # there is surely a safer way of doing this!
        if not self.source_ref_file[0] == "/":
            self.source_ref_file = os.path.join(self.cwd, self.source_ref_file)

        if not os.path.exists(self.source_ref_file):
            with open(self.source_ref_file, "w") as file:
                csvwriter = csv.DictWriter(file, fieldnames=["sequence", "timestamp", "source_ref"])
                csvwriter.writeheader()
                csvwriter.writerow({'sequence':0, 'timestamp':datetime.utcnow().isoformat(), 'source_ref': ""})


    def create_table_if_not_exists(self):

        raise NotImplemented


    def get_devicekey(self):
        key_file = os.path.join(self.cwd, self.device_key_file)
        try:
            f = open(key_file)
            device_key = f.read()
        except:
            print('Device Key cannot be found')
            return

        if len(device_key) != 20:
            print("Invalid Device Key")
            return

        return device_key

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

    def read_settings(self, settings_file):

        with open(settings_file) as file:
            settings = yaml.load(file, Loader=yaml.FullLoader)

        return settings

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

            headers = {'Authorization': 'Bearer ' + self.device_key}

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

        headers = {f'Authorization': 'Bearer {self.device_key}'}

        response = requests.post(f"{self.settings['API']}/quarantine_request/" ,
                                 data=payload,
                                 headers=headers)

        if response.status_code == 200:
            creds = json.loads(response.content)
        else:
            raise ValueError(f"Quaratine request FAILED: {response.reason}")

        # add device key - this can be removed when gascloud is updated to include this
        creds['destination'] += f"{self.device_key}/inbox/"

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
                    username=self.device_key,
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

