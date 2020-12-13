from gascloud.gascloud import Batcher
from devices.ocpn3 import OPCN3
import time
import os
from pathlib import Path



def main():

    settings_file = os.path.join(Path.cwd(), "settings.yaml")
    source = OPCN3(settings_file=settings_file)
    pi = Batcher(settings_file=settings_file, datasource=source)

    # make batch of current data and put it in pending diretory
    key = pi.make_batch()
    print(f"Made batch to upload with batch id {key}")



if __name__ == '__main__':
    main()


