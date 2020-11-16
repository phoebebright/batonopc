from devices.ocpn3 import OPCN3
import time
import os
from pathlib import Path


def main():

    settings_file = os.path.join(Path.cwd(), "settings.yaml")

    pi = OPCN3(settings_file)
    pi.create_readings_file()

    #TODO: handle no readings file

    # make batch from current readings.csv

    starttime = time.time()
    while True:
        seconds = time.time() - starttime

        # make batch of current data and put it in pending diretory
        key = pi.make_batch()

        # upload everything still in the pending directory
        pi.upload_all()

        print(f"uploading for {int(seconds)} seconds")
        # time.sleep(10)










if __name__ == '__main__':
    main()


