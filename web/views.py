from django.views.generic.base import TemplateView
from gadgetdb.models import Gadget

class Landing(TemplateView):

    template_name = "index.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['gadgets'] =  Gadget.objects.filter(status=Gadget.STATUS_ACTIVE)
        else:
            context['gadgets'] = ''

        return context

