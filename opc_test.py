'''this code is a low level test to check we wake up the OPCN3.
Next try read_once_opcn3 to use more features of the library'''

from usbiss.spi import SPI
import opc

# Open a SPI connection
spi = SPI("/dev/ttyACM0")

# Set the SPI mode and clock speed
spi.mode = 1
spi.max_speed_hz = 500000

try:
    alpha = opc.OPCN3(spi)
except Exception as e:
    print("Startup Error: {}".format(e))

# Turn on the OPC
alpha.on()

# Read the histogram and print to console
for key, value in alpha.histogram().items():
    print("Key: {}\tValue: {}".format(key, value))

# Shut down the opc
alpha.off()