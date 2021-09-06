import json

from django.utils import timezone
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
from rest_framework.decorators import (action, api_view,
                                       authentication_classes,
                                       permission_classes, throttle_classes)
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


    queryset = Reading.objects.all().select_related('gadget')
    serializer_class = ReadingSerializer
    filter_class = ReadingFilter

    def get_queryset(self):

        if self.action == "latest":
            return Reading.objects.order_by('gadget_id', '-timestamp').distinct('gadget_id')
        else:
            return  Reading.objects.all().select_related('gadget')

    @action(detail=False, methods=['get'])
    def latest(self, request, pk=None):
        '''call to latest will change the queryset used'''
        return self.list(request, pk)

class ReadingLatestViewset(ReadingViewset):

    queryset = Reading.objects.order_by('gadget_id', '-timestamp').distinct('gadget_id')



class ReadingsImportViewset(viewsets.ModelViewSet):
    '''used to send bulk readings'''
    authentication_classes = [SessionAuthentication, ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ReadingBulkImportSerializer
    queryset = Reading.objects.all()
    parser_classes = [JSONParser]
    http_method_names = ['post',]

    def create(self, request, *args, **kwargs):
        # there must be a drf way of doing this - need to parse readings to json
        data = request.data
        if type(data['readings']) != type([]):
            data['readings'] = json.loads(request.data['readings'])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        gadget, _ = Gadget.objects.get_or_create(factory_id=validated_data['gadget_id'], defaults={
            'created': timezone.now,
            'creator': request.user,
        })
        times = None
        for reading in validated_data['readings']:
            #TODO: if gadget != reading gadget - raise alarm
            times = reading['timestamp']
            del reading['gadget_id']
            del reading['timestamp']

            Reading.objects.update_or_create(gadget_id=gadget.id, timestamp=times, defaults=reading)

        # bump last_received_data field in gadget if applicable
        if times:
            gadget.last_received_data = times
            gadget.save(update_fields=['last_received_data'])

        # check gadget created date was added
        assert gadget.created != None

        return Response({'created':len(validated_data['readings'])}, status=status.HTTP_201_CREATED)