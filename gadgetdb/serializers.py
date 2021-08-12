from rest_framework import serializers
from .models import *

from django.contrib.auth import get_user_model

User = get_user_model()

import logging
logger = logging.getLogger('django')



class GadgetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gadget
        fields = '__all__'



    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['owner'] = str(instance.owner)
        ret['creator'] = str(instance.creator)
        ret['is_setup'] = "Y" if instance.is_setup() else ""
        ret['status'] = instance.get_status_display()
        ret['gadget_model'] = str(instance.gadget_model)
        return ret

class GadgetShortSerializer(GadgetSerializer):

    class Meta:
        model = Gadget
        fields = ['created', 'updated', 'ref', 'factory_id', 'status',
              'last_received_data', 'creator']

class GadgetFactoryIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gadget
        fields = ['factory_id',]

class GadgetLogSerializer(serializers.ModelSerializer):

    '''
       gadget = models.ForeignKey(Gadget, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default=ACTION_UPDATED)
    action = models.CharField(max_length=255)
    image = models.ImageField(upload_to="gadgets/images", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    when = models.DateTimeField(auto_now_add=True, db_index=True)
    where = models.CharField(max_length=20, blank=True, null=True)
    who = models.ForeignKey(OrgUser, blank=True, null=True, related_name="who_user", on_delete=models.CASCADE)

    media_type = models.CharField(max_length=3, default="IMG", db_index=True)
    store = models.CharField(max_length=50, default="local", blank=True, null=True,
                             help_text="Where media is currently stored - locally, Object Store etc.")
    # media = models.CharField(max_length=120, help_text="Full name including path")

    # this holds the original file
    media = models.FileField(upload_to=media_directory_path, storage=PrivateUploadStorage(), blank=True, null=True)
    # use this for display - links to reduced image if required
    media_url = models.CharField(max_length=200, blank=True, null=True)

    '''
    class Meta:
        model = GadgetLog
        fields = ('gadget_ref','action_type', 'action', 'notes', 'when', 'where', 'creator', 'created',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['creator'] = str(instance.creator)
        ret['factory_id'] = instance.gadget.factory_id
        return ret

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if not 'creator' in data and 'request' in self.context:
            data['creator'] = self.context['request'].user

        data['gadget'] = Gadget.objects.get(ref=data['gadget_ref'])

        return data

