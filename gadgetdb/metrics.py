
from django.utils import timezone

from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.views import APIView
from rest_framework import status

from datetime import timedelta

from .models import Gadget, GadgetLog
from .serializers import GadgetLogSerializer

class Metric(LoggingMixin, APIView):
    '''return metric active_gadgets'''
    http_method_names = ['get',]

    def get(self, request, *args, **kwargs):
        '''get the required metric'''


        if kwargs['metric'] == "active_gadgets":
            metric = active_gadgets(request.user)
        elif kwargs['metric'] == "active_gadgets_detail":
            metric = active_gadgets_detail(request.user)
        else:
            metric = None



        return Response(metric, status=status.HTTP_200_OK)

def active_gadgets_detail(user, gadget_type=None, days=30):
    '''count of gadgets that have successfully upload a file in the last n days'''

    end = timezone.now()
    start = timezone.now() - timedelta(days=days)

    # TODO: queryset based on user status

    gadgets = GadgetLog.objects.filter(when__range = (start, end), action_type=GadgetLog.ACTION_REPORTED).order_by('gadget','-when').distinct('gadget').values_list('gadget__factory_id', 'gadget__owner__name', 'gadget__gadget_model')

    return list(gadgets)

def active_gadgets(user, gadget_type=None, days=30):
    '''count of gadgets that have successfully upload a file in the last n days'''

    end = timezone.now()
    start = timezone.now() - timedelta(days=days)

    # TODO: queryset based on user status

    if user.is_gadget_admin() or user.is_workflow_user():
        queryset = GadgetLog.objects.all()
    else:
        queryset = GadgetLog.objects.filter(owner_key=user.organisation_id)

    # gadgets = queryset.filter(when__range=(start, end), action_type=GadgetLog.ACTION_REPORTED).order_by(
    #     'gadget', '-when').distinct('gadget')

    gadgets = queryset.filter(when__range=(start, end), action_type=GadgetLog.ACTION_REPORTED).order_by(
        'gadget_id', '-when').distinct('gadget_id',)

    if gadget_type:
        gadgets = gadgets.filter(gadget__gadget_model__gadget_type=gadget_type)

    return gadgets.count()



