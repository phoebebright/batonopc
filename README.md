# batonopc
OPC in Baton

Connecting a Raspberry Pi with OPC-N3 using USB
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

