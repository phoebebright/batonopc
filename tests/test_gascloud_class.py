from gascloud.gascloud import GasCloudInterface as GasCloud, DataSource

import os
import json
from pathlib import Path

class TestGasCloud:

    settings_file = os.path.join(Path.cwd(), "test_settings.yaml")
    gascloud = GasCloud(settings_file)

    def test_setup(self):
        '''check settings have been read'''
        assert self.gascloud.settings['BATCH_MODE'] == "PASS"

    def test_make_batch_one_device(self):
        pass
    def test_make_batch_multiple_devices(self):
        pass
    def test_quarantine_request(self):
        pass
    def test_upload_batch(self):
        pass
