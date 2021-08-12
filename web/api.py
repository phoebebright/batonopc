from rest_framework import filters, generics, mixins, status, viewsets
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)

from .models import Reading
from .serializers import ReadingSerializer

class ReadingViewset(viewsets.ModelViewSet):
    '''Testsheet issuers api'''
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer

