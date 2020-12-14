from gascloud.gascloud import Batcher
from devices.ocpn3 import OPCN3

import os




def main():

    settings_file = os.path.abspath("./settings.yaml")
    source = OPCN3(settings_file=settings_file)
    pi = Batcher(settings_file=settings_file, datasource=source)

    # make batch of current data and put it in pending diretory
    key = pi.make_batch()
    print(f"Made batch to upload with batch id {key}")



if __name__ == '__main__':
    main()


