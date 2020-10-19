# batonopc
OPC in Baton

Running test_opc.py
--------------------

Install requirements.txt

python3 test_opc.py

Expecting to hear fan start or change note, output displayed and fan stop.





INFORMATION ONLY - Connecting a Raspberry Pi with OPC-N3 using USB on PyCharm - the journey
------------------------------------------------

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




