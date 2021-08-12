from django.contrib import admin

from .models import *


class ReadingAdmin(admin.ModelAdmin):
    list_display = ('rdg_no','timestamp','gadget_id','temp', 'rh', 'pm_01', 'pm_10','pm_25')
    list_filter = ('timestamp','gadget_id',)

admin.site.register(Reading, ReadingAdmin)

