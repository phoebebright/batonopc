import json
from django.utils.dateparse import parse_date
from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db import models as django_models
from rest_framework.viewsets import ReadOnlyModelViewSet

from tools.auth import ApiKeyAuthentication
from .models import Reading
from gadgetdb.models import Gadget
from .serializers import ReadingSerializer, ReadingBulkImportSerializer

class ReadingFilter(filters.FilterSet):
    gadget = filters.CharFilter(field_name='gadget__factory_id', lookup_expr='iexact')
    class Meta:
        model = Reading
        fields = {
            'timestamp': ('lte', 'gte'),
        }

    filter_overrides = {
        django_models.DateTimeField: {
            'filter_class': filters.IsoDateTimeFilter
        },
    }



class ReadingViewset(ReadOnlyModelViewSet):
    '''single reading api'''

    authentication_classes = []
    permission_classes = []
    queryset = Reading.objects.all().select_related('gadget')
    serializer_class = ReadingSerializer
    filter_class = ReadingFilter







class ReadingsImportViewset(viewsets.ModelViewSet):
    '''used to send bulk readings'''
    authentication_classes = [SessionAuthentication, ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReadingBulkImportSerializer
    queryset = Reading.objects.all()
    parser_classes = [JSONParser]

    def create(self, request, *args, **kwargs):
        # there must be a drf way of doing this - need to parse readings to json
        data = request.data
        if type(data['readings']) != type([]):
            data['readings'] = json.loads(request.data['readings'])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        gadget, _ = Gadget.objects.get_or_create(factory_id=validated_data['gadget_id'])
        for reading in validated_data['readings']:
            #TODO: if gadget != reading gadget - raise alarm
            times = reading['timestamp']
            del reading['gadget_id']
            del reading['timestamp']

            Reading.objects.get_or_create(gadget_id=gadget.id, timestamp=times, defaults=reading)

        return Response({'created':len(validated_data['readings'])}, status=status.HTTP_201_CREATED)