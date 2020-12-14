from tinycloud.tinycloud import  Batcher, DataSource

from datetime import datetime

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('./opcn3.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

class OPCN3_SaveMixin(DataSource):
    '''define how data will be saved and format of sqlite table'''

    def create_table_if_not_exists(self):
        '''this format is for testing - each source of data will have it's own format'''

        sql = f'''
               CREATE TABLE IF NOT EXISTS {self.db_table} (
               rdg_no integer PRIMARY KEY AUTOINCREMENT,
               timestamp text NOT NULL,
               gadget_id REAL,
               temp REAL,
               rh REAL,
               pm01 REAL,
               pm25 REAL,
               pm10 REAL,
               raw_data VARCHAR
               );
               '''
        self.commit_sql(sql)

    def write_reading(self, gadget_id, **readings):

        timestamp = datetime.now()

        sql = f'''
               INSERT INTO {self.db_table} 
                 ('timestamp','gadget_id','temp','rh','pm01','pm25','pm10','raw_data')
               VALUES ('{timestamp:%Y-%m-%d %H:%M}',
                 '{gadget_id}', 
                 {readings['temp']},
                 {readings['rh']},
                 {readings['pm01']},
                 {readings['pm25']},
                 {readings['pm10']},
                 '{readings['raw_data']}')
               '''
        self.commit_sql(sql)


class OPCN3Batcher(Batcher, OPCN3_SaveMixin):
    '''connect database to the library for uploading to the cloud'''
