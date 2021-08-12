from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import RequestsClient
from rest_framework.test import APIClient
from django.test import TestCase, override_settings
from django.test import TestCase, Client


from tb_tools.testing_tools import  assertDatesMatch as eqdt_,eq_, ok_

from web.models import *

from gadgetdb.models import Gadget
from web.tests.test_api import BaseTestCase

class TestGadgets(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.url = "/api/v1/gadget/"


    def test_auth_required(self):

        # fails without auth
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_403_FORBIDDEN)

        # succeeds with auth
        response = self.client.get(self.url, headers={"Authorization": f"HTTP_BAT_API_KEY {self.api_key}"}, format='json')
        eq_(response.status_code, status.HTTP_200_OK)



