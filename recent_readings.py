from tinycloud.tinycloud import DataSource

import os

def main():
    '''display last 10 readings'''

    settings_file = os.path.abspath("settings.yaml")

    readingsdb = DataSource(settings_file = settings_file)

    for item in readingsdb.get_recent_readings():

        print(item)








if __name__ == '__main__':
    main()




