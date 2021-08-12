from datetime import date, datetime, timedelta

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

        self.api_key, self.key = APIKey.objects.create_key(name="test-key")

        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        cls.systemuser = CustomUser.system_user()



class TestWriteReadings(BaseTestCase):
    
    def test_add_reading(self):
        pass

    