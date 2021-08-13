from django.db import models

from yamlfield.fields import YAMLField
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.core.files.storage import FileSystemStorage



from tb_tools.model_mixins import CreatedMixin, CreatedUpdatedMixin, ModelDiffMixin, DataQualityMixin


import yaml
import os

import uuid

import logging
logger = logging.getLogger('django')




class Gadget_QuerySet(models.QuerySet):

    pass

class Gadget(CreatedUpdatedMixin):
    # this is based on the full BaseGadget in tb_devices in the toolbox but with far less fields

    STATUS_OUT_OF_SERVICE = "_"
    STATUS_ACTIVE = "A"
    STATUS_REDUNDENT = "R"
    STATUS_SPARE = "S"
    STATUS_TEST = "T"
    STATUS_UNKNOWN = "U"  # used when unrecognised gadgets are created by the system
    STATUS_CHOICES = (
        (STATUS_OUT_OF_SERVICE, "Out of Service"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_REDUNDENT, "Redundent"),
        (STATUS_TEST, "Test Mode"),
        (STATUS_SPARE, "Spare"),
        (STATUS_UNKNOWN, "Unknown"),
    )
    DEFAULT_STATUS = STATUS_OUT_OF_SERVICE

    ref = models.UUIDField(editable=False)

    factory_id = models.CharField(max_length=100, unique=True, help_text=_("BT ID"))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=DEFAULT_STATUS)
    last_received_data = models.DateTimeField(blank=True, null=True, help_text=_("Automatically updated if data received via gascloud"))

    notes = models.TextField(blank=True, null=True)



    objects = Gadget_QuerySet().as_manager()

    def __str__(self):
        return self.factory_id

    def save(self, *args, **kwargs):

        if not self.ref:
            self.ref = uuid.uuid4()


        super().save(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'creator', None) is None:
            obj.creator = request.user
        else:
            obj.updator = request.user
            obj.updated = timezone.now()
        obj.save()

class GadgetLog(CreatedMixin):

        ACTION_NOTE = "Note"
        ACTION_ALERT = "Alert"
        ACTION_SEEN = "Seen"
        ACTION_SETUP = "Setup"
        ACTION_ISSUED = "Issued"
        ACTION_SHIPPED = "Shipped"
        ACTION_RETURNED = "Returned"
        ACTION_LOCATED = "Location Change"
        ACTION_UPDATED = "Updated"
        ACTION_UPDATED_CALIBRATION = "Updated Calibration"
        ACTION_NEW_BATTERIES = "New Batteries"
        ACTION_BATTERY_LEVEL_REPORT = "Battery Level"
        ACTION_ADMIN_NOTE = "Admin info collected"
        ACTION_REPORTED = "Data Received"
        ACTION_SANDBOX = "Test Data Received"

        ACTION_TYPES = (
            (ACTION_SETUP, ACTION_SETUP),
            (ACTION_UPDATED, ACTION_UPDATED),
            (ACTION_ISSUED, ACTION_ISSUED),
            (ACTION_SHIPPED, ACTION_SHIPPED),
            (ACTION_RETURNED, ACTION_RETURNED),
            (ACTION_LOCATED, ACTION_LOCATED),
            (ACTION_NEW_BATTERIES, ACTION_NEW_BATTERIES),
            (ACTION_BATTERY_LEVEL_REPORT, ACTION_BATTERY_LEVEL_REPORT),
            (ACTION_UPDATED_CALIBRATION, ACTION_UPDATED_CALIBRATION),
            (ACTION_ADMIN_NOTE, ACTION_ADMIN_NOTE),
            (ACTION_SEEN, ACTION_SEEN),
            (ACTION_ALERT, ACTION_ALERT),
            (ACTION_REPORTED, ACTION_REPORTED),
            (ACTION_SANDBOX, ACTION_SANDBOX),
            (ACTION_NOTE, ACTION_NOTE),
        )

        gadget = models.ForeignKey("Gadget", on_delete=models.CASCADE)
        gadget_ref = models.UUIDField(db_index=True)
        action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default=ACTION_UPDATED)
        action = models.CharField(max_length=255)
        image = models.ImageField(upload_to="gadgets/images", blank=True, null=True)
        notes = models.TextField(blank=True, null=True)

        when = models.DateTimeField(default=timezone.now, db_index=True)
        where = models.CharField(max_length=20, blank=True, null=True)

        # note that we cannot have a relation with OrgUser via id as this can be different in different apps
        # currently username is not always filled in so can't make username the pk in OrgUser
        who = models.CharField(max_length=36, blank=True, null=True, help_text=_("Foreign Key to user via username"))

        batchid = models.CharField(max_length=32, db_index=True, blank=True, null=True)

        def __str__(self):
            return "%s - %s" % (self.gadget, self.action)



        def save(self, *args, **kwargs):

            if not self.gadget_ref:
                self.gadget_ref = self.gadget.ref

            super().save(*args, **kwargs)

        @classmethod
        def add_with_ref(cls, ref, *args, **kwargs):
            raise NotImplemented
            # gadget = Gadget.objects.get(ref=ref)
            #
            # cls.objects.create(
            #     gadget=gadget,
            #     **kwargs)

        @classmethod
        def add_with_gadget(cls, gadget, *args, **kwargs):
            '''use if you have the gadget object'''

            cls.objects.create(
                gadget=gadget,
                gadget_ref=gadget.ref,
                **kwargs)

        @property
        def admin_only(self):
            return self.action in [self.ACTION_ADMIN_NOTE, ]

