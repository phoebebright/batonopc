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

    