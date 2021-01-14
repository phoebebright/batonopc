from devices.opcn3_batcher import OPCN3Batcher
import time
import os
from pathlib import Path



def main():

    settings_file = os.path.abspath("settings.yaml")

    gc = OPCN3Batcher(settings_file=settings_file)
    msg = gc.upload_all()
    print(msg)


if __name__ == '__main__':
    main()


