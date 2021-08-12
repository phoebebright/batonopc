"""
WSGI config for tuning project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "/home/django/skorie/config/google-creds.json")

app_path = os.path.dirname(os.path.abspath(__file__)).replace('/config', '')
sys.path.append(app_path)
#activate_this = os.path.expanduser("/home/django/virtualenvs/ktotback/bin/activate_this.py")
#execfile(activate_this, dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# add this block of code
try:
    import uwsgidecorators
    from django.core.management import call_command

    @uwsgidecorators.timer(10)
    def send_queued_mail(num):
        """Send queued mail every 10 seconds"""
        call_command('send_queued_mail', processes=1)

except ImportError:
    print("uwsgidecorators not found. Cron and timers are disabled")