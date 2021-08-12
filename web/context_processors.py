from django.conf import settings


def include_settings(request=None):
    """
    add settings related to environment
    """

    return {'DEBUG': settings.DEBUG,
            'LANGUAGE_CODE': settings.LANGUAGE_CODE,
            'VERSION' : settings.VERSION,
            'SITE_URL' : settings.SITE_URL,
            'SITE_NAME' : settings.SITE_NAME,
            'user': request.user,
            'request': request,
            'API_URL': settings.API_URL,
            # 'MONITORING_URL': settings.MONITORING_URL,
            # 'HELP_URL': settings.HELP_URL,
            'LOGO_URL': settings.LOGO_URL,

            }

