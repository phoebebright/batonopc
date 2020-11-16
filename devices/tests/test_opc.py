from gascloud.gascloud import GasCloudInterface as GasCloud, DataSource

import os
import json
from pathlib import Path


class TestOPC:

    source = None
    readings1 = {'temp': 15.6, 'rh': 67.9, 'pm1': 5, 'pm25': 6, 'pm10': 3, 'raw_data':json.dumps({'bin1':5, 'bin2': 1})}
    gadget_id = "TEST"

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



    def test_add_one_reading(self):
        ''' '''

        # check readings record written
        self.source.write_reading(self.gadget_id,**self.readings1)


        rec = self.source.read_last(self.gadget_id)

        assert rec['gadget_id'] == self.readings1['gadget_id']
        assert rec['temp'] == self.readings1['temp']
        assert rec['rh'] == self.readings1['rh']
        assert rec['raw_data'] == self.readings1['raw_data']


