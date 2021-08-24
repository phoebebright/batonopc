import copy
import json
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
from gadgetdb.models import Gadget

logger = logging.getLogger('django')

class ReadingSerializer(serializers.ModelSerializer):


    # rec_no = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    gadget_id = serializers.CharField()
    temp = serializers.FloatField()
    rh = serializers.FloatField()
    samplingperiod = serializers.FloatField(required=False)
    sampleflowrate = serializers.FloatField(required=False)
    rejectcountglitch = serializers.FloatField(required=False)
    rejectcountlong = serializers.FloatField(required=False)
    pm_01 = serializers.FloatField()
    pm_25 = serializers.FloatField()
    pm_10 = serializers.FloatField()
    bin_0 = serializers.FloatField(required=False)
    bin_1 = serializers.FloatField(required=False)
    bin_2 = serializers.FloatField(required=False)
    bin_3 = serializers.FloatField(required=False)
    bin_4 = serializers.FloatField(required=False)
    bin_5 = serializers.FloatField(required=False)
    bin_6 = serializers.FloatField(required=False)
    bin_7 = serializers.FloatField(required=False)
    bin_8 = serializers.FloatField(required=False)
    bin_9 = serializers.FloatField(required=False)
    bin_10 = serializers.FloatField(required=False)
    bin_11 = serializers.FloatField(required=False)
    bin_12 = serializers.FloatField(required=False)
    bin_13 = serializers.FloatField(required=False)
    bin_14 = serializers.FloatField(required=False)
    bin_15 = serializers.FloatField(required=False)
    bin1_mtof = serializers.FloatField(required=False)
    bin3_mtof = serializers.FloatField(required=False)
    bin5_mtof = serializers.FloatField(required=False)
    bin7_mtof = serializers.FloatField(required=False)

    samplingperiod = serializers.FloatField(required=False)
    sampleflowrate = serializers.FloatField(required=False)
    rejectcountglitch = serializers.FloatField(required=False)
    rejectcountlong = serializers.FloatField(required=False)
    # validation = serializers.CharField(required=False, allow_blank=True)
    # valid = serializers.BooleanField(required=False)

    class Meta:
        model = Reading
        fields = ('timestamp','gadget_id','temp','rh','pm_01','pm_25','pm_10','bin_0','bin_1','bin_2','bin_3','bin_4','bin_5','bin_6','bin_7','bin_8','bin_9','bin_10','bin_11','bin_12','bin_13','bin_14','bin_15','bin1_mtof','bin3_mtof','bin5_mtof','bin7_mtof','samplingperiod','sampleflowrate','rejectcountglitch','rejectcountlong')


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['gadget_id'] = instance.gadget.factory_id
        return ret

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        return ret

class ReadingBulkImportSerializer(serializers.Serializer):

    gadget_id = serializers.CharField(required=True)
    readings = ReadingSerializer(many=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['gadget_id'] = instance.gadget.factory_id
        return ret

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        return ret