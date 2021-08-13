from django.contrib import admin

from .models import *


class GadgetAdmin(admin.ModelAdmin):
    list_display = ('factory_id',)
    # list_filter = ('timestamp','gadget_id',)

admin.site.register(Gadget, GadgetAdmin)

