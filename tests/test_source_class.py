from tinycloud.tinycloud import Batcher as GasCloud, DataSource
import pytest
import os
import json
from pathlib import Path

TEST_SETTINGS = {
    'DBNAME': './test_readings.db',
    'DB_TABLE': 'Readings',
    'GADGET_ID': 'TST_001',
}

class TestDataSource:


    source = None

    def setup_method(self):
        #':memory:'
        self.source = DataSource(TEST_SETTINGS)
        self.source.connect2db()

    def teardown_method(self):
        self.source.db.close()


    def test_setup(self):
        '''check settings have been read'''
        assert self.source.settings['GADGET_ID'] == TEST_SETTINGS['GADGET_ID']
        os.remove('./test_readings.db')

    def test_pass_settings_as_dict(self):

        settings = {'DBNAME': 'different_readings.db', 'DB_TABLE': 'OtherReadings', 'GADGET_ID': "OTHER"}
        sauce = DataSource(settings)

        assert sauce.settings['DBNAME'] == 'different_readings.db'
        assert sauce.settings['DB_TABLE'] == 'OtherReadings'
        assert sauce.settings['GADGET_ID'] == 'OTHER'

    def test_settings_dict_overrides_files(self):

        settings = {'DBNAME': 'different_readings.db', 'DB_TABLE': 'OtherReadings', 'GADGET_ID': "OTHER"}
        sauce = DataSource(settings, settings_file="./test_settings/test_settings.yaml")

        assert sauce.settings['DBNAME'] == 'different_readings.db'
        assert sauce.settings['DB_TABLE'] == 'OtherReadings'
        assert sauce.settings['GADGET_ID'] == 'OTHER'

    def test_default_settings_file_used(self):

        sauce = DataSource()

        assert sauce.settings['DBNAME'] == 'default.db'
        assert sauce.settings['DB_TABLE'] == 'DefaultReadings'

    def test_missing_settings_file(self):

        with pytest.raises(ValueError):
            sauce = DataSource(settings_file="pepper.yaml")


    def test_create_db_if_not_exists(self):

        if os.path.exists('./test_readings.db'):
            os.remove('./test_readings.db')

        new_source = DataSource(settings_file="test_settings/test_settings.yaml")
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

        new_source = DataSource(settings_file="test_settings/test_settings.yaml")
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

