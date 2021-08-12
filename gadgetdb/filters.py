from rest_framework_datatables.django_filters.backends import DatatablesFilterBackend
from rest_framework_datatables.django_filters.filterset import DatatablesFilterSet
from rest_framework_datatables.django_filters.filters import GlobalFilter
from django_filters import rest_framework as filters
from .models import GadgetLog

class GlobalCharFilter(GlobalFilter, filters.CharFilter):
    pass


class GadgetLogGlobalFilter(DatatablesFilterSet):

    batchid = GlobalCharFilter(lookup_expr='icontains')
    action = GlobalCharFilter(lookup_expr='icontains')
    action_type = GlobalCharFilter(lookup_expr='icontains')
    notes = GlobalCharFilter(lookup_expr='icontains')


    class Meta:
        model = GadgetLog
        fields = ['action','action_type', 'notes', 'batchid']
