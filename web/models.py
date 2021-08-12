
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