from gascloud.ocpn3 import OPCN3

import time
import csv
import os
from pathlib import Path





def main():



    settings_file = os.path.join(Path.cwd(), "settings.yaml")

    pi = OPCN3(settings_file)
    pi.create_readings_file()

    with open(pi.readings_file_path, "a") as file:
        csvwriter = csv.DictWriter(file, fieldnames=['rtype', 'seconds','temperature','rh','pm01','pm25','pm10'])

        starttime = time.time()

        pi.wake()

        done = False
        while not done:

            try:
                seconds = time.time() - starttime
                reading = pi.get_particulates()

                pi.write_reading({'rtype': 10, 'seconds': seconds,
                                  'temperature': reading['temperature'],
                                  'rh': reading['rh'],
                                  'pm01': reading['pm01'],
                                  'pm25': reading['pm25'],
                                  'pm10': reading['pm10'],
                                  }, csvwriter)



                print(f"logging for {int(seconds)} seconds")
                time.sleep(60)

            except KeyboardInterrupt:
                done = True
                pi.sleep()


if __name__ == '__main__':
    main()

