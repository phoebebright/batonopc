# batonopc
This is a code library to assist in collecting data from the Alphasense OPCN3 and pushing it to a cloud for processing.  

The generic code is in the tinycloud directory and code specific to the OPC is int he devices directory.  This code is split into the opcn3.py - for reading data and storing it to a database and opcn3_batcher for batching up the data in the database and sending it to the cloud.

There are examples of how to use the code in .py files at the root level and these are listed in getting started below.


Assumptions
------------
This documentation is currently assuming the OPC3 is the only device being collected from but the code has been structured in a way that adding additional devices should not be hard.

Time resolution is 1 second.  It is assumed that sub-second readings are not required.

The library is currently setup to write data to https://tinycloud.purit.ie  - a login and gateway key are required to do this.


Getting started
---------------

Install requirements.txt

    pip3 install -r requirements.txt
    
    
Testing connection to the OPCN3
--------------------

Connect OPCN3 to power and via USB to the pi

    python3 opc_test.py

Expecting to hear fan start or change note, output displayed and fan stops.

Note: ZeroDivisionError: float division by zero
is caused by bad coding - just run again!

Check there is a settings.yaml file and try:

    python3 read_once_opcn3.py
    
Expecting to see a single reading displayed, eg.

logging None t:20.0, rh: 52.0, pms: 1.4, 2.6, 6.3
    
You may get a message: Gateway Key cannot be found
The gateway key is requried when uploading to the cloud, but for now it can be ignored.

    
    
Collecting Data
----------------
To create a database and start logging::

    python3 log_data.py
    
Data is logged to an sqlite database every 10 secs while program runs

Get latest reading from the database
-----------------

    python3 recent_readings.py
    
Display 10 recent readings

Prepare to upload data to Tinycloud
-------------------------

A valid gateway_key.txt file is required and this is created by registering the pi with tinycloud.  This requires logging into Tinycloud and selecting Get a Pin.
Register the pin by running

    python3 tinycloud/register.py

You will be asked to enter the pin and the pin will be verified with tinycloud (so must be online to do this).  The gateway_key.txt will be automatically created.  Running register again will overwrite this file.

Make a batch of data for Tinycloud
-------------------------

Now a batch can be created from readings in the readings database as a result of running log_data.py.

    python3 make_batch.py
    
Creates a directory batches2upload and puts a zip file containing data ready to upload.


Upload to Tinycloud
-------------------

    python3 pi_to_cloud.py

Push any batches in batches2upload to the cloud.  Must have registered the pi as a gateway device with tinycloud and being using a valid gadget_id.


Automate logging and uploading
--------
Cron jobs can be created to periodically call log_data.py, make_batch.py and pi_to_cloud.py or this code can be used as example code for customised integration.


New Device Setup
===============

/devices
Each new data source/device can be customised in terms of how data is collected and where it is written.  See opcn3.py 
Each new device can be added to this directory.

/tinycloud
Each device inherits from DataSource class in the gascloud directory which has methods for saving and uploading data.  

example files are provided at the root level.  These can be used as a template of how to interact with the library.






INFORMATION ONLY - Connecting a Raspberry Pi with OPC-N3 using USB on PyCharm - the journey
===========

The first challenge is there is not some out of the box code (that I can find Oct 2020) to do this.

This code works with usb (and spi) but is only for N2

    https://github.com/dhhagan/py-opc

This code works with spi for N3

    https://github.com/south-coast-science/scs_dfe_eng



py-opc

This code runs with errors::

    from usbiss.spi import SPI
    import opc
    
    # Open a SPI connection
    spi = SPI("/dev/ttyACM0")
    
    # Set the SPI mode and clock speed
    spi.mode = 1
    spi.max_speed_hz = 500000
    
    try:
        alpha = opc.OPCN2(spi)
    except Exception as e:
        print ("Startup Error: {}".format(e))
    
    # Turn on the OPC
    alpha.on()
    
    # Read the histogram and print to console
    for key, value in alpha.histogram().items():
        print ("Key: {}\tValue: {}".format(key, value))
    
    # Shut down the opc
    alpha.off()
    

ERROR:opc:Could not parse the fimrware version from ????????????????????????????????????????????????????????????

Comment in issues

@biogis Yea, I would say that's expected. When you initiate an instance of OPCN2, it automatically issues the read_info_string() method to get the firmware version so that it knows which other methods are unavailable. For the OPCN2's, the firmware versions were in the range 15-18.2; however, on the OPCN3's, they switched it up, and now the firmware versions are stuck in v1 (i.e. v1.17) - not sure why they did that...

Anyways, as far as I can tell, they changed all of the SPI commands and added an extra command byte which means that none of the old code will work - some of it is similar, but the one I don't understand is how to turn the device on and off, which is kind of important...



Install this repo/branch instead

    pip3 install git+https://github.com/lizcorson/py-opc@opc-n3
    
    
and change alpha = opc.OPCN2(spi) to alpha = opc.OPCN3(spi)


and magic!

    Key: Bin 0	Value: 0.0
    Key: Bin 1	Value: 0.0
    Key: Bin 2	Value: 0.0
    Key: Bin 3	Value: 0.0
    Key: Bin 4	Value: 0.0
    Key: Bin 5	Value: 0.0
    Key: Bin 6	Value: 0.0
    Key: Bin 7	Value: 0.0
    Key: Bin 8	Value: 0.0
    Key: Bin 9	Value: 0.0
    Key: Bin 10	Value: 0.0
    Key: Bin 11	Value: 0.0
    Key: Bin 12	Value: 0.0
    Key: Bin 13	Value: 0.0
    Key: Bin 14	Value: 0.0
    Key: Bin 15	Value: 0.0
    Key: Bin 16	Value: 0.0
    Key: Bin 17	Value: 0.0
    Key: Bin 18	Value: 0.0
    Key: Bin 19	Value: 0.0
    Key: Bin 20	Value: 0.0
    Key: Bin 21	Value: 0.0
    Key: Bin 22	Value: 0.0
    Key: Bin 23	Value: 0.0
    Key: Bin1 MToF	Value: 0.0
    Key: Bin3 MToF	Value: 0.0
    Key: Bin5 MToF	Value: 0.0
    Key: Bin7 MToF	Value: 0.0
    Key: Sampling Period	Value: 43.87
    Key: Sample Flow Rate	Value: 3.69
    Key: Temperature	Value: 22.50057221332112
    Key: Relative humidity	Value: 46.749065384908825
    Key: PM_A	Value: 0.0
    Key: PM_B	Value: 0.0
    Key: PM_C	Value: 0.0
    Key: Reject count Glitch	Value: 0
    Key: Reject count LongTOF	Value: 0
    Key: Reject count Ratio	Value: 0
    Key: Reject Count OutOfRange	Value: 0
    Key: Fan rev count	Value: 0
    Key: Laser status	Value: 608
    Key: Checksum	Value: 44240




