from tinycloud.tinycloud import Batcher , DataSource

import os
import json
from pathlib import Path

TEST_SETTINGS = {
    'DBNAME': './test_readings.db',
    'DB_TABLE': 'Readings',
    'GASCLOUD_KEY': 'DEMO',
    'GADGET_ID': 'TST_001',
    'GADGET_TYPE': 'OPCN3',
    'UPLOAD_INTERVAL_SECS': 3600,   # how often batches are uploaded
    'LOGGING_INTERVAL_SECS': 300,   # how often data is collected from the device
    'BATCH_MODE': 'PASS',
    'BATCH_TYPE': 'OPC',
    'BATCH_DIR_PENDING': './batches2upload',
    'BATCH_DIR_UPLOADED': './batchesuploaded',
    'DELETE_BATCH_ON_UPLOAD': False,
    'DELETE_READING_ON_ZIP': False,
}

class TestGasCloud:


    batcher = Batcher(TEST_SETTINGS)
    source = DataSource(TEST_SETTINGS)
    source.connect2db()

    def test_setup(self):
        '''check settings have been read'''
        assert self.batcher.settings['BATCH_MODE'] == "PASS"


    def test_get_gateway_key(self):

        assert self.batcher.get_gatewaykey() == "11794317e05a4cb3befb"

    def test_make_batch(self):

        json_data = json.dumps([{'1': 1, '2': '2'}])
        self.source.write_reading("TEST", temp=1.1, rh=2.2, raw_data=json_data)
        json_data = json.dumps([{'1': 2, '2': '3'}])
        self.source.write_reading("TEST", temp=1.2, rh=2.3, raw_data=json_data)

        key = self.batcher.make_batch()

        assert key == "11794317e05a4cb3befb"


    def test_quarantine_request(self):
        pass
    def test_upload_batch(self):
        pass
