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

        self.url = "/api/v1/gadget/"
        super().setUp()
        self.client.credentials(HTTP_AUTHORIZATION=f"HTTP_BAT_API_KEY {self.key}")


    def test_add_gadget(self):

        payload = {'factory_id': "gadget1"}
        response = self.client.post(self.url, payload, format='json')
        eq_(response.status_code, status.HTTP_201_CREATED)



