from devices.ocpn3 import OPCN3


import time
import csv
import os
from pathlib import Path





def main():


    settings_file = os.path.join(Path.cwd(), "settings.yaml")

    pi = OPCN3(settings_file)
    pi.connect2db()


    starttime = time.time()

    pi.wake()

    done = False
    print("Logging started.  Press Ctrl-C to stop.")
    while not done:

        try:

            reading = pi.get_particulates()

            pi.write_reading(pi.gadget_id, **reading)

            print(f"logging  t:{reading['temp']}, rh: {reading['rh']}, pms: {reading['pm01']}, {reading['pm25']}, {reading['pm10']}")
            time.sleep(10)

        except KeyboardInterrupt:
            done = True
            pi.sleep()

        except Exception as e:
            print(f"Error {e}")


if __name__ == '__main__':
    main()

