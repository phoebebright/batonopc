
#
import logging
import os
import random
#import beeline
import django
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser

from django.db import IntegrityError, models
from django.db.models import Q
from django.db.models.signals import m2m_changed
from django.forms.models import model_to_dict
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_time
from django.utils.text import get_valid_filename
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _
from django.db.models import F, Subquery
from django.template.loader import render_to_string

from gadgetdb.models import Gadget

logger = logging.getLogger('django')
testlog = logging.getLogger('testsheets')

# timezone_countries = {timezone: country
#                                   for country, timezones in pytz.country_timezones.data.items()
#                                   for timezone in timezones}

#TODO: add reversion
#TODO: ripple down published flag - in particular how is published in import handled?
#TODO: Check that report_id column is included as required by dashboard


class ModelDiffMixin(object):
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super().save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                                           self._meta.fields])




class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):

    email = models.EmailField(_('email address'), unique=True)
    username = None
    removed_date = models.DateTimeField(blank=True, null=True)



    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @classmethod
    def system_user(cls):
        # need a dummy person instance

        system_user, _ = cls.objects.get_or_create(email="system@batondata.co.uk")
        return system_user

class Reading(models.Model):
    rdg_no = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(db_index=True)
    gadget = models.ForeignKey(Gadget, on_delete=models.CASCADE)
    temp = models.FloatField(blank=True, null=True)
    rh = models.FloatField(blank=True, null=True)
    pm_01 = models.FloatField(blank=True, null=True)
    pm_25 = models.FloatField(blank=True, null=True)
    pm_10 = models.FloatField(blank=True, null=True)
    bin_0 = models.FloatField(blank=True, null=True)
    bin_1 = models.FloatField(blank=True, null=True)
    bin_2 = models.FloatField(blank=True, null=True)
    bin_3 = models.FloatField(blank=True, null=True)
    bin_4 = models.FloatField(blank=True, null=True)
    bin_5 = models.FloatField(blank=True, null=True)
    bin_6 = models.FloatField(blank=True, null=True)
    bin_7 = models.FloatField(blank=True, null=True)
    bin_8 = models.FloatField(blank=True, null=True)
    bin_9 = models.FloatField(blank=True, null=True)
    bin_10 = models.FloatField(blank=True, null=True)
    bin_11 = models.FloatField(blank=True, null=True)
    bin_12 = models.FloatField(blank=True, null=True)
    bin_13 = models.FloatField(blank=True, null=True)
    bin_14 = models.FloatField(blank=True, null=True)
    bin_15 = models.FloatField(blank=True, null=True)
    bin_16 = models.FloatField(blank=True, null=True)
    bin_17 = models.FloatField(blank=True, null=True)
    bin_18 = models.FloatField(blank=True, null=True)
    bin_19 = models.FloatField(blank=True, null=True)
    bin_20 = models.FloatField(blank=True, null=True)
    bin_21 = models.FloatField(blank=True, null=True)
    bin_22 = models.FloatField(blank=True, null=True)
    bin_23 = models.FloatField(blank=True, null=True)

    bin1_mtof = models.FloatField(blank=True, null=True)
    bin3_mtof = models.FloatField(blank=True, null=True)
    bin5_mtof = models.FloatField(blank=True, null=True)
    bin7_mtof = models.FloatField(blank=True, null=True)

    samplingperiod = models.FloatField(blank=True, null=True)
    sampleflowrate = models.FloatField(blank=True, null=True)
    rejectcountglitch = models.FloatField(blank=True, null=True)
    rejectcountlong = models.FloatField(blank=True, null=True)
    # reject_count_ratio = models.FloatField(blank=True, null=True)
    # reject_count_outofrange = models.FloatField(blank=True, null=True)
    # fan_rev_count = models.FloatField(blank=True, null=True)
    # last_status = models.FloatField(blank=True, null=True)
    # checksum = models.FloatField(blank=True, null=True)

    def __str__(self):
        return str(self.rdg_no)