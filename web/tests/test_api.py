from datetime import date, datetime, timedelta
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

        self.fred = CustomUser.objects.create_user("fred@batcondata.co.uk", "pass")
        self.external = CustomUser.objects.create_user("test@batondata.co.uk", 'pass')
        self.api_key, self.key = APIKey.objects.create_key(name=self.external.email)
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        cls.systemuser = CustomUser.system_user()

    def test_auth_required(self):

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

class TestWriteReadings(BaseTestCase):
    
    def test_add_reading(self):
        pass

class TestBulkImportReadings(BaseTestCase):

    def setUp(self):

        self.url = "/api/v1/readings/"
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f"HTTP_BAT_API_KEY {self.key}")


    def test_import(self):

        payload = {'gadget_id': 'OPC R2', 'readings': [{'rec_no': 1, 'gadget_id': 'OPC R2', 'temp': 37.4, 'rh': 17.6, 'samplingperiod': 30.2, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 42.0, 'pm01': 1.6, 'pm25': 11.2, 'pm10': 122.0, 'bin_0': 1613, 'bin_1': 197, 'bin_2': 240, 'bin_3': 10, 'bin_4': 5, 'bin_5': 4, 'bin_6': 3, 'bin_7': 284, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 1, 'bin1_mtof': 56, 'bin3_mtof': 81, 'bin5_mtof': 99, 'bin7_mtof ': 112, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:40:00'}, {'rec_no': 2, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.5, 'samplingperiod': 7.5, 'sampleflowrate': 5.5, 'rejectcountglitch': 206.0, 'rejectcountlong': 9.0, 'pm01': 1.8, 'pm25': 12.2, 'pm10': 121.3, 'bin_0': 365, 'bin_1': 45, 'bin_2': 79, 'bin_3': 5, 'bin_4': 3, 'bin_5': 2, 'bin_6': 1, 'bin_7': 71, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 59, 'bin3_mtof': 90, 'bin5_mtof': 87, 'bin7_mtof ': 119, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:41:00'}, {'rec_no': 3, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.6, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 10.0, 'pm01': 3.1, 'pm25': 13.4, 'pm10': 125.5, 'bin_0': 1366, 'bin_1': 51, 'bin_2': 64, 'bin_3': 3, 'bin_4': 2, 'bin_5': 1, 'bin_6': 2, 'bin_7': 73, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 66, 'bin3_mtof': 84, 'bin5_mtof': 129, 'bin7_mtof ': 111, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:41:00'}, {'rec_no': 4, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.7, 'samplingperiod': 7.7, 'sampleflowrate': 5.5, 'rejectcountglitch': 94.0, 'rejectcountlong': 13.0, 'pm01': 1.3, 'pm25': 11.1, 'pm10': 135.6, 'bin_0': 236, 'bin_1': 33, 'bin_2': 69, 'bin_3': 2, 'bin_4': 0, 'bin_5': 0, 'bin_6': 2, 'bin_7': 74, 'bin_8': 1, 'bin_9': 0, 'bin_10': 2, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 55, 'bin3_mtof': 90, 'bin5_mtof': 0, 'bin7_mtof ': 113, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:42:00'}, {'rec_no': 5, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.7, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 33.0, 'rejectcountlong': 6.0, 'pm01': 1.3, 'pm25': 11.2, 'pm10': 128.9, 'bin_0': 180, 'bin_1': 54, 'bin_2': 58, 'bin_3': 6, 'bin_4': 0, 'bin_5': 1, 'bin_6': 0, 'bin_7': 74, 'bin_8': 0, 'bin_9': 0, 'bin_10': 1, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 48, 'bin3_mtof': 70, 'bin5_mtof': 72, 'bin7_mtof ': 113, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:42:00'}, {'rec_no': 6, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 91.0, 'rejectcountlong': 10.0, 'pm01': 1.9, 'pm25': 12.0, 'pm10': 121.8, 'bin_0': 563, 'bin_1': 37, 'bin_2': 67, 'bin_3': 6, 'bin_4': 2, 'bin_5': 0, 'bin_6': 2, 'bin_7': 72, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 58, 'bin3_mtof': 79, 'bin5_mtof': 0, 'bin7_mtof ': 116, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:43:00'}, {'rec_no': 7, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.7, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 34.0, 'rejectcountlong': 12.0, 'pm01': 1.3, 'pm25': 11.8, 'pm10': 122.8, 'bin_0': 161, 'bin_1': 35, 'bin_2': 67, 'bin_3': 5, 'bin_4': 5, 'bin_5': 2, 'bin_6': 0, 'bin_7': 73, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 52, 'bin3_mtof': 91, 'bin5_mtof': 84, 'bin7_mtof ': 117, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:43:00'}, {'rec_no': 8, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 34.0, 'rejectcountlong': 10.0, 'pm01': 1.3, 'pm25': 11.0, 'pm10': 115.4, 'bin_0': 179, 'bin_1': 70, 'bin_2': 54, 'bin_3': 6, 'bin_4': 0, 'bin_5': 3, 'bin_6': 1, 'bin_7': 68, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 50, 'bin3_mtof': 90, 'bin5_mtof': 78, 'bin7_mtof ': 113, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:44:00'}, {'rec_no': 9, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 25.0, 'rejectcountlong': 10.0, 'pm01': 1.3, 'pm25': 10.8, 'pm10': 121.5, 'bin_0': 155, 'bin_1': 57, 'bin_2': 59, 'bin_3': 5, 'bin_4': 0, 'bin_5': 0, 'bin_6': 0, 'bin_7': 73, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 51, 'bin3_mtof': 82, 'bin5_mtof': 0, 'bin7_mtof ': 113, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:44:00'}, {'rec_no': 10, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.7, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 12.0, 'pm01': 1.8, 'pm25': 11.3, 'pm10': 119.8, 'bin_0': 558, 'bin_1': 61, 'bin_2': 55, 'bin_3': 1, 'bin_4': 1, 'bin_5': 1, 'bin_6': 1, 'bin_7': 71, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 52, 'bin3_mtof': 81, 'bin5_mtof': 107, 'bin7_mtof ': 111, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:45:00'}, {'rec_no': 11, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.7, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 35.0, 'rejectcountlong': 9.0, 'pm01': 1.2, 'pm25': 10.8, 'pm10': 120.7, 'bin_0': 162, 'bin_1': 55, 'bin_2': 56, 'bin_3': 3, 'bin_4': 1, 'bin_5': 0, 'bin_6': 1, 'bin_7': 72, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 53, 'bin3_mtof': 66, 'bin5_mtof': 0, 'bin7_mtof ': 114, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:45:00'}, {'rec_no': 12, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 37.0, 'rejectcountlong': 11.0, 'pm01': 1.4, 'pm25': 10.7, 'pm10': 115.3, 'bin_0': 160, 'bin_1': 74, 'bin_2': 58, 'bin_3': 4, 'bin_4': 2, 'bin_5': 0, 'bin_6': 0, 'bin_7': 69, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 50, 'bin3_mtof': 92, 'bin5_mtof': 0, 'bin7_mtof ': 116, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:46:00'}, {'rec_no': 13, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 45.0, 'rejectcountlong': 11.0, 'pm01': 1.4, 'pm25': 11.3, 'pm10': 117.6, 'bin_0': 155, 'bin_1': 53, 'bin_2': 68, 'bin_3': 7, 'bin_4': 4, 'bin_5': 0, 'bin_6': 0, 'bin_7': 70, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 53, 'bin3_mtof': 80, 'bin5_mtof': 0, 'bin7_mtof ': 115, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:46:00'}, {'rec_no': 14, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 43.0, 'rejectcountlong': 10.0, 'pm01': 1.3, 'pm25': 11.3, 'pm10': 123.5, 'bin_0': 171, 'bin_1': 36, 'bin_2': 70, 'bin_3': 4, 'bin_4': 1, 'bin_5': 2, 'bin_6': 0, 'bin_7': 72, 'bin_8': 1, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 52, 'bin3_mtof': 77, 'bin5_mtof': 87, 'bin7_mtof ': 114, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:47:00'}, {'rec_no': 15, 'gadget_id': 'OPC R2', 'temp': 37.0, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 30.0, 'rejectcountlong': 8.0, 'pm01': 1.3, 'pm25': 11.6, 'pm10': 121.0, 'bin_0': 183, 'bin_1': 38, 'bin_2': 67, 'bin_3': 7, 'bin_4': 1, 'bin_5': 2, 'bin_6': 2, 'bin_7': 71, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 50, 'bin3_mtof': 72, 'bin5_mtof': 79, 'bin7_mtof ': 116, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:47:00'}, {'rec_no': 16, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 12.8, 'sampleflowrate': 5.5, 'rejectcountglitch': 159.0, 'rejectcountlong': 11.0, 'pm01': 1.5, 'pm25': 11.2, 'pm10': 120.8, 'bin_0': 522, 'bin_1': 82, 'bin_2': 116, 'bin_3': 2, 'bin_4': 3, 'bin_5': 1, 'bin_6': 1, 'bin_7': 120, 'bin_8': 1, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 53, 'bin3_mtof': 72, 'bin5_mtof': 94, 'bin7_mtof ': 115, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:49:00'}, {'rec_no': 17, 'gadget_id': 'OPC R2', 'temp': 37.4, 'rh': 17.5, 'samplingperiod': 20.3, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 16.0, 'pm01': 1.9, 'pm25': 11.9, 'pm10': 130.7, 'bin_0': 1601, 'bin_1': 107, 'bin_2': 186, 'bin_3': 5, 'bin_4': 4, 'bin_5': 2, 'bin_6': 1, 'bin_7': 196, 'bin_8': 1, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 2, 'bin1_mtof': 53, 'bin3_mtof': 83, 'bin5_mtof': 59, 'bin7_mtof ': 115, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:51:00'}, {'rec_no': 18, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.6, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 36.0, 'rejectcountlong': 15.0, 'pm01': 1.4, 'pm25': 11.5, 'pm10': 116.2, 'bin_0': 163, 'bin_1': 34, 'bin_2': 81, 'bin_3': 4, 'bin_4': 2, 'bin_5': 3, 'bin_6': 2, 'bin_7': 66, 'bin_8': 1, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 56, 'bin3_mtof': 82, 'bin5_mtof': 94, 'bin7_mtof ': 117, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:52:00'}, {'rec_no': 19, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.7, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 12.0, 'pm01': 3.8, 'pm25': 13.4, 'pm10': 120.1, 'bin_0': 1757, 'bin_1': 53, 'bin_2': 65, 'bin_3': 5, 'bin_4': 1, 'bin_5': 0, 'bin_6': 1, 'bin_7': 70, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 65, 'bin3_mtof': 71, 'bin5_mtof': 0, 'bin7_mtof ': 112, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:52:00'}, {'rec_no': 20, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 16.0, 'pm01': 2.8, 'pm25': 13.1, 'pm10': 133.8, 'bin_0': 1009, 'bin_1': 49, 'bin_2': 80, 'bin_3': 4, 'bin_4': 1, 'bin_5': 0, 'bin_6': 1, 'bin_7': 75, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 1, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 52, 'bin3_mtof': 72, 'bin5_mtof': 0, 'bin7_mtof ': 113, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:53:00'}, {'rec_no': 21, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 255.0, 'rejectcountlong': 9.0, 'pm01': 2.7, 'pm25': 11.8, 'pm10': 115.9, 'bin_0': 1070, 'bin_1': 46, 'bin_2': 71, 'bin_3': 3, 'bin_4': 1, 'bin_5': 0, 'bin_6': 0, 'bin_7': 67, 'bin_8': 1, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 69, 'bin3_mtof': 108, 'bin5_mtof': 0, 'bin7_mtof ': 114, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:53:00'}, {'rec_no': 22, 'gadget_id': 'OPC R2', 'temp': 37.1, 'rh': 17.8, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 35.0, 'rejectcountlong': 12.0, 'pm01': 1.3, 'pm25': 11.7, 'pm10': 123.5, 'bin_0': 196, 'bin_1': 32, 'bin_2': 73, 'bin_3': 6, 'bin_4': 0, 'bin_5': 3, 'bin_6': 1, 'bin_7': 73, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 58, 'bin3_mtof': 67, 'bin5_mtof': 109, 'bin7_mtof ': 115, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:54:00'}, {'rec_no': 23, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.8, 'samplingperiod': 8.2, 'sampleflowrate': 5.5, 'rejectcountglitch': 229.0, 'rejectcountlong': 9.0, 'pm01': 1.9, 'pm25': 11.8, 'pm10': 120.8, 'bin_0': 549, 'bin_1': 40, 'bin_2': 86, 'bin_3': 3, 'bin_4': 3, 'bin_5': 0, 'bin_6': 0, 'bin_7': 78, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 56, 'bin3_mtof': 79, 'bin5_mtof': 0, 'bin7_mtof ': 116, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:54:00'}, {'rec_no': 24, 'gadget_id': 'OPC R2', 'temp': 37.2, 'rh': 17.7, 'samplingperiod': 7.6, 'sampleflowrate': 5.5, 'rejectcountglitch': 36.0, 'rejectcountlong': 8.0, 'pm01': 1.2, 'pm25': 10.9, 'pm10': 116.8, 'bin_0': 175, 'bin_1': 59, 'bin_2': 53, 'bin_3': 2, 'bin_4': 3, 'bin_5': 1, 'bin_6': 2, 'bin_7': 69, 'bin_8': 0, 'bin_9': 0, 'bin_10': 0, 'bin_11': 0, 'bin_12': 0, 'bin_13': 0, 'bin_14': 0, 'bin_15': 0, 'bin1_mtof': 50, 'bin3_mtof': 72, 'bin5_mtof': 77, 'bin7_mtof ': 115, 'validation': '', 'valid': True, 'timestamp': '2021-06-05T13:55:00'}]}


        response = self.client.post(self.url, data=payload, format='json')
        eq_(response.status_code, status.HTTP_201_CREATED)
