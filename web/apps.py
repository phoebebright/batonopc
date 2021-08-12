
from django.apps import AppConfig
from django.conf import settings
#import beeline

class WebConfig(AppConfig):
    name = 'web'

    def ready(self):
        import web.signals

        # if settings.HONEYCOMBE:
        #
        #       # If you use uwsgi, gunicorn, celery, or other pre-fork models, see the section below on pre-fork
        #       # models and do not initialize here.
        #         beeline.init(
        #             writekey=settings.HONEYCOMBE_KEY,
        #             dataset='skorie',
        #             service_name='skorie',
        #             debug=True,
        #         )