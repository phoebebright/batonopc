from devices.ocpn3 import OPCN3  # import class for data source

import time
import csv
import os
from pathlib import Path
import yaml



def main():

   # open my custom settings file for this particular OPCN3
   settings_file = os.path.join(Path.cwd(), "example_settings.yaml")

   # instantiate the class with these settings and wake up the device
   item = OPCN3(settings_file)
   item.wake()

   # give OPC a chance to collect some data
   time.sleep(5)

   # get the readings
   reading = item.get_particulates()

   print(f"logging {item.gadget_id} t:{reading['temp']}, rh: {reading['rh']}, pms: {reading['pm01']}, {reading['pm25']}, {reading['pm10']}")


if __name__ == '__main__':
   main()
