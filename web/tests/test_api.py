from datetime import date, datetime, timedelta
from django.utils import dateparse
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
from tools.testing_tools import eq_, ok_
from rest_framework.test import APIClient, APITestCase, RequestsClient
from rest_framework_api_key.models import APIKey

from tools.testing_tools import assertDatesMatch as eqdt_
from web.models import *


User = get_user_model()

NOW = timezone.now()
TODAY_STARTS = NOW.replace(hour=0, minute=0, second=0)
TODAY_ENDS = NOW.replace(hour=23, minute=59, second=59)
YESTERDAY = NOW - timedelta(days=1)
TOMORROW = NOW + timedelta(days=1)
NEXTWEEK = NOW + timedelta(days=7)
LASTWEEK = NOW - timedelta(days=7)
NEXTMONTH = NOW + timedelta(days=31)
LASTMONTH = NOW + timedelta(days=31)
TRIALENDS = TODAY_ENDS + timedelta(days=7)


class BaseTestCase(APITestCase):
    url = None

    def setUp(self) -> None:
        super().setUp()

        self.gadget1 = Gadget.objects.create(factory_id='gadget1')
        self.gadget2 = Gadget.objects.create(factory_id='gadget2')


        Reading.objects.create(rdg_no=1, timestamp=YESTERDAY, gadget=self.gadget1, temp=10, rh=70, pm_01= 1.0, pm_25=2.5, pm_10=10)
        Reading.objects.create(rdg_no=2, timestamp=TODAY_STARTS, gadget=self.gadget1, temp=10, rh=70, pm_01= 1.1, pm_25=2.6, pm_10=10.1)

        self.fred = CustomUser.objects.create_user("fred@batcondata.co.uk", "pass")
        self.external = CustomUser.objects.create_user("test@batondata.co.uk", 'pass')
        self.api_key, self.key = APIKey.objects.create_key(name=self.external.email)

        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        cls.systemuser = CustomUser.system_user()

class TestAuth(BaseTestCase):

    def test_auth_required_for_batch_import(self):

        self.url = "/api/v1/readings/"
        payload = {'gadget_id': 'OPC R2', 'readings': [
            {'rec_no': 5, 'gadget_id': 'OPC R2', 'temp': 37.4, 'rh': 17.6, 'samplingperiod': 30.2, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 42.0, 'pm_01': 1.6, 'pm_25': 11.2, 'pm_10': 122.0, 'bin_0': 1613, 'bin_1': 197, 'bin_2': 240, 'bin_3': 10, 'bin_4': 5, 'bin_5': 4, 'bin_6': 3, 'bin_7': 284, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 1, 'bin1_mtof': 56, 'bin3_mtof': 81, 'bin5_mtof': 99, 'bin7_mtof ': 112, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:40:00'},
            {'rec_no': 6, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.5, 'samplingperiod': 7.5, 'sampleflowrate': 5.5, 'rejectcountglitch': 206.0, 'rejectcountlong': 9.0, 'pm_01': 1.8, 'pm_25': 12.2, 'pm_10': 121.3, 'bin_0': 365, 'bin_1': 45, 'bin_2': 79, 'bin_3': 5, 'bin_4': 3, 'bin_5': 2, 'bin_6': 1, 'bin_7': 71, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 59, 'bin3_mtof': 90, 'bin5_mtof': 87, 'bin7_mtof ': 119, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:41:00'}]}

        # fails without auth
        response = self.client.post(self.url, data=payload,  format='json')
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

        # succeeds with authenticated user
        self.client.force_authenticate(user=self.fred)
        response = self.client.post(self.url, data=payload, format='json')
        eq_(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        # succeeds with auth token
        self.client.credentials(HTTP_AUTHORIZATION=f"HTTP_BAT_API_KEY {self.key}")
        response = self.client.post(self.url, data=payload, format='json')
        eq_(response.status_code, status.HTTP_201_CREATED)

    def test_no_get_on_bulk_import(self):

        self.url = "/api/v1/readings/"
        self.client.credentials(HTTP_AUTHORIZATION=f"HTTP_BAT_API_KEY {self.key}")
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_auth_required_for_list_readings(self):

        self.url = "/api/v1/reading/"

        # fails without auth
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

        # succeeds with authenticated user
        self.client.force_authenticate(user=self.fred)
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_200_OK)
        self.client.logout()

        # succeeds with auth token
        self.client.credentials(HTTP_AUTHORIZATION=f"HTTP_BAT_API_KEY {self.key}")
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_200_OK)


class TestReadReading(BaseTestCase):


    def setUp(self):

        self.url = "/api/v1/reading/"
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f"HTTP_BAT_API_KEY {self.key}")


    def test_get_all_readings(self):

        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(len(response.data), 2)
        reading1 = response.data[0]
        eq_(reading1['gadget_id'], self.gadget1.factory_id)

    def test_get_latest_readings(self):
        self.url = "/api/v1/reading/latest/"
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_200_OK)
        eq_(len(response.data), 1)
        eq_(dateparse.parse_datetime(response.data[0]['timestamp']), TODAY_STARTS)

class TestBulkImportReadings(BaseTestCase):

    def setUp(self):

        self.url = "/api/v1/readings/"
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f"HTTP_BAT_API_KEY {self.key}")


    def test_import(self):

        payload = {'gadget_id': 'OPC R2', 'readings': [
            {'rec_no': 3, 'gadget_id': 'OPC R2', 'temp': 37.4, 'rh': 17.6, 'samplingperiod': 30.2, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 42.0, 'pm_01': 1.6, 'pm_25': 11.2, 'pm_10': 122.0, 'bin_0': 1613, 'bin_1': 197, 'bin_2': 240, 'bin_3': 10, 'bin_4': 5, 'bin_5': 4, 'bin_6': 3, 'bin_7': 284, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 1, 'bin1_mtof': 56, 'bin3_mtof': 81, 'bin5_mtof': 99, 'bin7_mtof ': 112, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:40:00'},
            {'rec_no': 4, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.5, 'samplingperiod': 7.5, 'sampleflowrate': 5.5, 'rejectcountglitch': 206.0, 'rejectcountlong': 9.0, 'pm_01': 1.8, 'pm_25': 12.2, 'pm_10': 121.3, 'bin_0': 365, 'bin_1': 45, 'bin_2': 79, 'bin_3': 5, 'bin_4': 3, 'bin_5': 2, 'bin_6': 1, 'bin_7': 71, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 59, 'bin3_mtof': 90, 'bin5_mtof': 87, 'bin7_mtof ': 119, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:41:00'}]}

        response = self.client.post(self.url, data=payload, format='json')
        eq_(response.status_code, status.HTTP_201_CREATED)
