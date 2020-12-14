from tinycloud.tinycloud import Batcher
import time
import os
from pathlib import Path



def main():

    settings_file = os.path.join(Path.cwd(), "settings.yaml")

    gc = Batcher(settings_file)
    gc.upload.all()
    print(f"uploading")


if __name__ == '__main__':
    main()


