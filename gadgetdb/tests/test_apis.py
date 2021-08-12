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
from web.api import BaseTestCase

class TestMyGadgets(GasCloudAPITestCase):

    def setUp(self):
        super().setUp()
        self.url = "/api/v1/my_gadgets/"




    def test_auth_required(self):

        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_admin_sees_all(self):

        all = Gadget.objects.all().count()

        self.client.login(username=self.superman, password='supermanblue')
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_200_OK)

        eq_(len(response.data), all)

    def test_customer_sees_only_their_org(self):

        self.client.login(username='mary@tinycloud.purit.ie', password='maryred')
        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_200_OK)

        eq_(len(response.data), 2)
        assert 'RED1' in response.data
        assert 'RED2' in response.data


    def test_device_key_auth(self):

        device = Device.add_device(self.datauser_2)
        key = device.activate()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + key)

        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_200_OK)

        eq_(len(response.data), 2)
        assert 'RED1' in response.data
        assert 'RED2' in response.data

class TestUpdateBaseline(GasCloudAPITestCase):

    def setUp(self):
        super().setUp()
        self.gadget = self.gadget_red_1
        self.url = f"/api/v1/gadget/{self.gadget.factory_id}/update_baseline/"

    def test_auth_required(self):

        response = self.client.get(self.url, format='json')
        eq_(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_valid(self):

        eq_(self.gadget.calibration['we0'], 5)

        self.client.login(username=self.superman, password='supermanblue')
        response = self.client.patch(self.url, format='json', data = {'baseline': 10})
        eq_(response.status_code, status.HTTP_200_OK)

        # check updated
        self.gadget.refresh_from_db()

        eq_(self.gadget.calibration['we0'], 10)
