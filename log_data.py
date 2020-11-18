from devices.ocpn3 import OPCN3


import time
import csv
import os
from pathlib import Path
import yaml




def main():


    settings_file = os.path.join(Path.cwd(), "settings.yaml")
    with open(settings_file) as file:
        settings = yaml.load(file, Loader=yaml.FullLoader)

    # setup each data source
    sources = []
    for source in settings['DATA_SOURCES']:


        item = OPCN3(source['settings'])
        item.wake()

        sources.append(item)


    starttime = time.time()

    for source in sources:
        print(source.read_last(source.gadget_id))

    done = False
    print("Logging started.  Press Ctrl-C to stop.")
    while not done:
        for  source in sources:
            try:

                reading = source.get_particulates()
                source.write_reading(source.gadget_id, **reading)

                print(f"logging {source.gadget_id} t:{reading['temp']}, rh: {reading['rh']}, pms: {reading['pm01']}, {reading['pm25']}, {reading['pm10']}")


            except KeyboardInterrupt:
                done = True
                source.sleep()

            except Exception as e:
                print(f"Error {e}")

        time.sleep(10)

if __name__ == '__main__':
    main()

