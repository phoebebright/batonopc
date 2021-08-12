from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin


from django_ace import AceWidget

import csv
from datetime import datetime


from .models import Gadget
from .forms import GadgetLogForm
from .metrics import active_gadgets_detail


class GadgetList(LoginRequiredMixin, TemplateView):
    template_name = "gadgetdb/gadget_list.html"




class GadgetDetail(LoginRequiredMixin, DetailView):
    model = Gadget

    def get_object(self):
        try:
            return Gadget.objects.get(ref=self.kwargs['pk'])
        except:
            return Gadget.objects.get(factory_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # create a form for adding to the log
        context['log_form'] = GadgetLogForm(initial={'gadget_id':self.object.id})

        try:
            context['current_we_baseline'] = self.object.calibration['we0']
            context['current_ae_baseline'] = self.object.calibration['ae0']
            context['current_sensitivity'] = self.object.calibration['sensitivity_nappm']
        except:
            context['current_we_baseline'] = 0
            context['current_ae_baseline'] = 0
            context['current_sensitivity'] = 0


        return context
