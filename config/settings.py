"""
Django settings for ktotback project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib.messages import constants as messages




SETUP = "PRODUCTION"
SITE_ID = 1
SITE_URL = "https://batondata.co.uk"
SITE_NAME = "Baton Data"


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#ROOT_DIR = environ.Path(__file__) - 3  # (skorie/config/settings/base.py - 3 = skorie/)


VERSION = "0.0.1 August 2021"
API_VERSION = "001"
API_URL = "https://batondata.co.uk/"
LOGO_URL = ''

SECRET_KEY = "ABCD"


DEBUG = False
USE_ASSETS = True


# prevents this error: *kwasync)#012django.db.utils.OperationalError: FATAL:  remaining connection slots are reserved for non-replication superuser connections
CONN_MAX_AGE = None

ALLOWED_HOSTS = ['batondata.co.uk','www.batondata.co.uk',  ]


AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `keycloak`
    # this can create a problem where the webfront end knows the user is logged in but accessing an API does
    # not pass the user in.
    "django.contrib.auth.backends.ModelBackend",

)



AUTH_USER_MODEL = "web.CustomUser"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

# # tastypie is trying to load geo libraries
# GDAL_LIBRARY_PATH = '/usr/lib/ogdi/libgdal.so'

POST_OFFICE = {
    'DEFAULT_PRIORITY': 'now',
    'LOG_LEVEL': 2,
}

DEFAULT_AUTO_FIELD='django.db.models.AutoField'
# DATABASE_ROUTERS = ['config.dbrouters.HelpdeskRouter', ]

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'web.middleware.IDSubomainRequestMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',


    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django_user_agents.middleware.UserAgentMiddleware',


]




INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django_countries',


    # "post_office",
    'django_filters',
    'rest_framework',
    "rest_framework_api_key",
    'csvexport',
    # 'theme',

    'gadgetdb',
    'web',

]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'


LANGUAGE_CODE = 'en-GB'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True



LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
APPEND_SLASH = True


ADMINS = [('Phoebe','phoebebright310@gmail.com'),('Phoebe','phoebe@skor.ie'), ]
MANAGERS = ADMINS
DEFAULT_FROM_EMAIL = "Skor.ie <info@skor.ie>"
DEFAULT_TO_EMAIL = "info@skor.ie"
SUPPORT_EMAIL = "info@skor.ie"
NOTIFY_NEW_USER_EMAILS = "phoebebright310@gmail.com"

EMAIL_BACKEND = 'post_office.EmailBackend'

MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

# Static files (CSS, JavaScript, Images)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

)

STATIC_ROOT = os.path.join(BASE_DIR, 'shared_static')  # this may well be changed in settings_local in production
STATIC_URL = '/static/'



# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/uploads/'



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),


                 ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': False,
            'context_processors': [

                'django.template.context_processors.debug',

                'django.template.context_processors.request',
                # "allauth.account.context_processors.account",
                # "allauth.socialaccount.context_processors.socialaccount",
                # 'countries_plus.context_processors.add_request_country',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web.context_processors.include_settings',
            ],
        },
    },
]

# # countries_plus - will only work once you have country code already -
#
# COUNTRIES_PLUS_COUNTRY_HEADER = 'HTTP_CF_COUNTRY'
# COUNTIRES_PLUS_DEFAULT_ISO = 'IE'

COUNTRIES_ONLY = ['US', 'GB', 'IE', 'AU', 'NZ','CA']




# ALLAUTH settings
#
#
# SOCIALACCOUNT_PROVIDERS = {
#     'whinie_oa2': {
#         'PROVIDER_URL': 'https://api.whin.ie/o',
#         'SCOPE': ['read', 'write', 'introspection'],  # remove introspection once worked out how to get email in complete_login
#     },
#     'facebook': {
#         'METHOD': 'oauth2',
#         'SCOPE': ['email', 'public_profile'],
#         'AUTH_PARAMS': {'auth_type': 'https'},
#         #'AUTH_PARAMS': {'auth_type': 'reauthenticate'},  this will require people re-enter their password in facebook
#         'INIT_PARAMS': {'cookie': True},
#         'FIELDS': [
#             'id',
#             'email',
#             'first_name',
#             'last_name',
#         ],
#         'EXCHANGE_TOKEN': True,
#         # 'LOCALE_FUNC': 'path.to.callable',
#         'VERIFIED_EMAIL': False,
#         'VERSION': 'v2.12',
#     }
# }
#
# SOCIALACCOUNT_ADAPTER = 'web.views.DCSocialAccountAdapter'

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_EMAIL_VERIFICATION = "none"   # currently using custom signup if not facebook

SOCIAL_AUTH_POSTGRES_JSONFIELD = True


# TEMPLATE_CONTEXT_PROCESSORS = TEMPLATES[0]['OPTIONS']['context_processors']   # keeps allauth happy

# Registration settings
# REGISTRATION_AUTO_LOGIN = True
# ACCOUNT_ACTIVATION_DAYS = 7


REST_FRAMEWORK = {


    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        # "rest_framework_api_key.permissions.HasAPIKey",
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',

    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),

}
API_KEY_CUSTOM_HEADER = "HTTP_BAT_API_KEY"


# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

#
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'formatters': {
#         'standard': {
#             'format': '%(levelname)s %(asctime)s %(module)s  %(message)s'
#         },
#         "post_office": {
#             "format": "[%(levelname)s]%(asctime)s PID %(process)d: %(message)s",
#             "datefmt": "%d-%m-%Y %H:%M",
#         },
#     },
#
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard',
#         },
#         'logfile': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.RotatingFileHandler',
#             'maxBytes': 1024 * 1024 * 5,  # 5 MB
#             'backupCount': 5,
#             'filename': os.path.join(BASE_DIR, "logs/django.log"),
#             'formatter': 'standard',
#         },
#
#
#         # 'email': {
#         #     'level': 'DEBUG',
#         #     'class': 'logging.handlers.RotatingFileHandler',
#         #     'maxBytes': 1024 * 1024 * 5,  # 5 MB
#         #     'backupCount': 5,
#         #     'filename': os.path.join(BASE_DIR, "logs/email.log"),
#         #     'formatter': 'standard',
#         # },
#
#         # "post_office": {
#         #     "level": "DEBUG",
#         #     'class': 'logging.handlers.RotatingFileHandler',
#         #     'maxBytes': 1024 * 1024 * 5,  # 5 MB
#         #     'backupCount': 5,
#         #     'filename': os.path.join(BASE_DIR, "logs/postoffice.log"),
#         #     "formatter": "post_office"
#         # },
#         # 'mail_admins': {
#         #     'level': 'ERROR',
#         #     'filters': ['require_debug_false'],
#         #     'class': 'django.utils.log.AdminEmailHandler'
#         # },
#
#         # everything that goes to syslog goes to papertrail https://papertrailapp.com/systems/1848252051/events
#         # 'SysLog': {
#         #     'level': 'DEBUG',
#         #     'class': 'logging.handlers.SysLogHandler',
#         #     'formatter': 'standard',
#         #     'address': ('logs6.papertrailapp.com', 34636)
#         # },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['logfile','console','SysLog'],
#             'level': 'INFO',
#             'propagate': True,
#         },
#
#
#         'email': {
#             'handlers': ['email', ],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#
#         # "post_office": {
#         #     "handlers": ["post_office",],
#         #     "level": "INFO"
#         # },
#
#         'javascript_error': {
#             'handlers': [ 'logfile','console','SysLog'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#         'django.utils.autoreload': {
#             'level': 'INFO',
#         },
#     },
# }


try:
    localpath=os.path.join(BASE_DIR, 'config/settings_local.py')
    print(localpath)
    if  os.path.exists(localpath):
        with open(localpath) as f:
            code = compile(f.read(), localpath, 'exec')
            exec(code, globals(), locals())


except Exception as e:
    print(e)
    print("No local settings found or error in settings_local.py")

