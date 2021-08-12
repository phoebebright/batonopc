import logging

from django.conf import settings
#from registration.signals import user_registered
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from post_office import mail

logger = logging.getLogger('email')

