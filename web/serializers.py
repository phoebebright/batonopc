import copy
import logging

from datetime import datetime

from django.utils import timezone
from django.utils.decorators import method_decorator
from django_countries.serializer_fields import CountryField
from django.conf import settings
from pytz import country_timezones
from rest_framework import serializers
from rest_framework.fields import JSONField, CurrentUserDefault

from .models import Reading

logger = logging.getLogger('django')

class ReadingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reading
        fields = '__all__'
