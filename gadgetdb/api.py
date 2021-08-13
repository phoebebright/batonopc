from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework_api_key.permissions import HasAPIKey
from tools.auth import ApiKeyAuthentication
from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.translation import ugettext_lazy as _

from .models import *
from .serializers import *
# from .metrics import active_gadgets_detail
from .filters import GadgetLogGlobalFilter

#TODO: move to toolbox/gadget_base

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class GadgetViewSet(viewsets.ModelViewSet):
    #permission_classes = [HasAPIKey | IsAuthenticated]
    authentication_classes = [SessionAuthentication, ApiKeyAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Gadget.objects.all()
    serializer_class = GadgetShortSerializer
    lookup_field = 'factory_id'
    pagination_class = None



    @action(detail=True, methods=['post'])
    def add2log(self, request, pk=None, factory_id=None):
        gadget = self.get_object()

        try:
            # why is this required?
            data = request.data.dict()
        except:
            data = request.data


        data['gadget'] = gadget.id
        data['creator'] = request.user.id

        # when - default to now
        if not 'when' in request.data:
            data['when'] = timezone.now()

        # who
        if 'who' in request.data:
            if request.data['who'] == request.user.email:
                data['who'] = data['creator']

        else:
            data['who'] = data['creator']

        serializer = GadgetLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    #
    # @action(detail=True, methods=['patch'])
    # def update_baseline(self, request, pk=None, factory_id=None):
    #     gadget = self.get_object()
    #
    #     kwargs = {}
    #     if 'we_baseline' in request.data:
    #         kwargs['we0'] = int(request.data['we_baseline'])
    #     if 'ae_baseline' in request.data:
    #         kwargs['ae0'] = int(request.data['ae_baseline'])
    #     if 'sensitivity' in request.data:
    #         kwargs['sensitivity'] = int(request.data['sensitivity'])
    #
    #     if kwargs:
    #         gadget.update_edt_calibrations(request.user, **kwargs)
    #
    #     return Response("OK")
    #


class GadgetLogViewset(viewsets.ModelViewSet):
    '''return list of log entries filtered according to gadget reference '''
    queryset = GadgetLog.objects.all()
    serializer_class = GadgetLogSerializer
    http_method_names = ['get','post']

    pagination_class = StandardResultsSetPagination
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['factory_id', 'action_type', 'action']
    # ordering_fields = ['factory_id', 'action_type', 'action', 'when', 'creator']
    # ordering = ['-when']



class GadgetLogListViewset(generics.ListAPIView):
    #TODO: this can probably be replaced by Uploads Viewset
    serializer_class = GadgetLogSerializer

    queryset = GadgetLog.objects.all().order_by('-when')
    http_method_names = ['get', ]
    filter_backends = (DatatablesFilterBackend,)
    filterset_class = GadgetLogGlobalFilter

    def get_queryset(self):
        '''queryset depends on user'''

        me = self.request.user

        gadget = Gadget.objects.get(ref=self.kwargs['gadget_ref'])

        # check this user can view this gadget
        if not gadget.can_view(me):
            return GadgetLog.objects.none()

        qs = GadgetLog.objects.filter(gadget_ref=self.kwargs['gadget_ref']).order_by('-when')


        return qs


class ActiveGadgets(APIView):
    '''list of recently seen gadgets for this user'''
    http_method_names = ['get',]

    def get(self, request, *args, **kwargs):

        active_gadgets = active_gadgets_detail(request.user, "EDT2")
        gadget_list = [g for (g, _, _) in active_gadgets]



        qs = Gadget.objects.filter(factory_id__in=gadget_list)
        serializer = GadgetSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

