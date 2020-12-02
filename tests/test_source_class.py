from gascloud.gascloud import GasCloudInterface as GasCloud, DataSource

import os
import json
from pathlib import Path


class TestDataSource:


    source = None

    def setup_method(self):
        #':memory:'
        self.source = DataSource("test_source1_settings.yaml")
        self.source.connect2db()

    def teardown_method(self):
        self.source.db.close()


    def test_setup(self):
        '''check settings have been read'''
        assert self.source.settings['UPLOAD_INTERVAL_SECS'] == 3600
        os.remove('./test_readings.db')

    def test_create_db_if_not_exists(self):

        if os.path.exists('./test_readings.db'):
            os.remove('./test_readings.db')

        new_source = DataSource("test_source1_settings.yaml")
        new_source.connect2db()

        assert os.path.exists('./test_readings.db')

        # check no records
        sql = f'SELECT * FROM {new_source.db_table}'

        result = new_source.db.execute(sql)

        assert result.lastrowid == 0

    def test_use_existing_db(self):

        # using the existing db, write one record
        assert os.path.exists('./test_readings.db')
        self.source.write_reading("TEST",temp=1,rh=2,raw_data="3")
        sql = f'SELECT * FROM {self.source.db_table}'
        result = self.source.db.execute(sql)
        assert result.lastrowid == 1

        # now close and reopen and make sure it is the same file

        new_source = DataSource("test_source1_settings.yaml")
        new_source.connect2db()

        assert os.path.exists('./test_readings.db')
        sql = f'SELECT * FROM {self.source.db_table}'
        result = self.source.db.execute(sql)
        assert result.lastrowid == 1

    def test_add_one_reading(self):
        ''' '''

        # check readings record written
        json_data = json.dumps([{'1':1, '2':'2'}])
        self.source.write_reading("TEST",temp=1.1,rh=2.2,raw_data=json_data)


        rec = self.source.read_last("TEST")

        assert rec['gadget_id'] == "TEST"
        assert rec['temp'] == 1.1
        assert rec['rh'] == 2.2
        assert rec['raw_data'] == json_data

        json_json = json.loads(rec['raw_data'] )
        assert json_json[0]['1'] == 1

    def test_get_gateway_key(self):

        assert self.source.get_gatewaykey() == "11794317e05a4cb3befb"

    def test_make_batch(self):

        json_data = json.dumps([{'1': 1, '2': '2'}])
        self.source.write_reading("TEST", temp=1.1, rh=2.2, raw_data=json_data)
        json_data = json.dumps([{'1': 2, '2': '3'}])
        self.source.write_reading("TEST", temp=1.2, rh=2.3, raw_data=json_data)

        key = self.source.make_batch()

        assert key == "11794317e05a4cb3befb"

