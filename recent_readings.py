from gascloud.gascloud import DataSource

import time
import os
from pathlib import Path


def main():

    settings_file = os.path.join(Path.cwd(), "settings.yaml")

    readingsdb = DataSource(settings_file)

    for item in readingsdb.get_recent_readings():

        print(item)








if __name__ == '__main__':
    main()




