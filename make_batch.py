
from devices.opcn3_batcher import  OPCN3Batcher

import os




def main():

    settings_file = os.path.abspath("settings.yaml")
    pi = OPCN3Batcher(settings_file=settings_file)

    #TODO: warn if no gateway key
    # make batch of current data and put it in pending directory
    batch_file = pi.make_batch()
    print(f"Made batch to upload: {batch_file}")



if __name__ == '__main__':
    main()


