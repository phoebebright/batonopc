
    
Uploading to gascloud
=======================



Setup
------

A gateway key is required to upload.  Get a pin number from your gascloud online application and run::

    python3 gascloud/register.py
      
Enter pin when requested.  This generates a gateway_key.txt file and the contents is used to upload.  Move the gateway_key.txt file into the root directory for the app. 

Your devices will have been registered with the gascloud system (OPCN3, EDT) on the Gadgets database. Add the id you receive as GADGET_ID in the settings. 

Check/create a settings.yaml, see example_settings.yaml for guidance.

Also change the UPLOAD_INTERVAL_SECS as required - this determines how often the data will be uploaded to the cloud, not how often it is logged from the sensors.


To upload, run pi_upload - this has a loop that calls the upload code then waits for the number of seconds set in UPLOAD_INTERVAL_SECS::

    python3 pi_upload.py
    
    
How it works
--------------

Data is collected from the readings.csv file and written as a new csv file with a new source reference.  The readings.csv is now cleared down.  A.yaml file is created with meta details and has the same filename as the csv file with the .yaml extension..  These two files are zipped up and put in a pending directory.  At the same time a new .yaml file is created with the content that will be needed to make a quarantine_request.

Upload then looks for all zips in the pending directory and for each one, makes a quarantine_request
 
    thegascloud.com/api/v1/quarantine_request/
    
With details of what is to be uploaded.  A batch id is returned and credentials for uploading.  These are available for 10 mins.  The batch can now be scp'd to the credentials provided.  If this is successful, the file is moved to an uploaded directory.

Settings
---------

Settings stored in settings.yaml 

API: https://thegascloud.com/api/v1 v#the api to use (production or test)
DBNAME: ./example.db                 #name of the local database that has the readings
GADGET_ID: TST_001                   #id of the raspberry pi that has been registered in the gadgets database
GASCLOUD_KEY: DEMO                   #not used yet but will be rquired to make initial register call
UPLOAD_INTERVAL_SECS: 300            #periods between uploads in seconds
BATCH_MODE: PASS                     #mode to use (LIVE, TEST or PASS)
BATCH_TYPE: OPC                      #type of data being uploaded
BATCH_DIR_PENDING: /home/pi/opc/batches2upload
BATCH_DIR_UPLOADED: /home/pi/opc/batchesuploaded
DELETE_BATCH_ON_UPLOAD: False        #delete the files once they have been uploaded successfully
DELETE_READING_ON_ZIP: False         #delete the readings from the database once the zip file has been created (but not uploaded)


    