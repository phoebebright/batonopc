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


VERSION = "2.1.4 August 2021"
API_VERSION = "214"

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
    'django_user_agents.middleware.UserAgentMiddleware',


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


    "post_office",
    'django_filters',
    'rest_framework',
    "rest_framework_api_key",

    'theme',


    'web',

]
CRISPY_TEMPLATE_PACK = 'bootstrap5'

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
    'compressor.finders.CompressorFinder',
)

STATIC_ROOT = os.path.join(BASE_DIR, 'shared_static')
STATIC_URL = '/shared_static/'

# compress both js and css - settings for django-compressor
COMPRESS_JS_FILTERS = ['compressor.filters.jsmin.SlimItFilter',]
COMPRESS_CSS_FILTERS = ['compressor.filters.cssmin.CSSCompressorFilter',]
COMPRESS_OFFLINE = False
COMPRESS_ENABLED = True

# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/uploads/'

EVENT_ROOT = os.path.join(BASE_DIR, 'events')
EVENT_URL = '/event_media/'

QR_ROOT = os.path.join(BASE_DIR, 'qr')
QR_URL = '/qr/'

ASSETS_ROOT = os.path.join(BASE_DIR, 'assets')
ASSETS_URL = '/assets/'

CHUNKED_UPLOAD_MAX_BYTES = 30*10000000

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR,  'templates/organiser'),
                 os.path.join(BASE_DIR,  'templates/competitor'),
                 os.path.join(BASE_DIR, 'templates/video'),

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


# django-helpdesk configuration settings
# You can override django-helpdesk's defaults by redefining them here.
# To see what settings are available, see the docs/configuration.rst
# file for more information.
# Some common settings are below.

HELPDESK_DEFAULT_SETTINGS = {
            'use_email_as_submitter': True,
            'email_on_ticket_assign': True,
            'email_on_ticket_change': True,
            'login_view_ticketlist': False,
            'email_on_ticket_apichange': True,
            'preset_replies': True,
            'tickets_per_page': 100
}

#HELPDESK_DEFAULT_TICKET_TYPE = "B"

HELPDESK_STAFF_ONLY_TICKET_OWNERS = True

HELPDESK_TEAMS = False

HELPDESK_USE_CDN = True

HELPDESK_USE_HTTPS_IN_EMAIL_LINK = True

# Should the public web portal be enabled?
HELPDESK_PUBLIC_ENABLED = False
HELPDESK_VIEW_A_TICKET_PUBLIC = False
HELPDESK_SUBMIT_A_TICKET_PUBLIC = False

# Should the Knowledgebase be enabled?
HELPDESK_KB_ENABLED = True

# Allow users to change their passwords
HELPDESK_SHOW_CHANGE_PASSWORD = True

# Instead of showing the public web portal first,
# we can instead redirect users straight to the login page.
HELPDESK_REDIRECT_TO_LOGIN_BY_DEFAULT = False


REST_FRAMEWORK = {


    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'django_keycloak.auth.backends.KeycloakDRFAuthorizationBackend',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),

}


# JSON_EDITOR_JS = 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/4.2.1/jsoneditor.js'
# JSON_EDITOR_CSS = 'https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/4.2.1/jsoneditor.css'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

HONEYCOMBE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(module)s  %(message)s'
        },
        "post_office": {
            "format": "[%(levelname)s]%(asctime)s PID %(process)d: %(message)s",
            "datefmt": "%d-%m-%Y %H:%M",
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/django.log"),
            'formatter': 'standard',
        },
        'calclog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, "logs/calc.log"),
            'formatter': 'standard',
        },
        'api': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/api.log"),
            'formatter': 'standard',
        },
        'contactlog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/contact.log"),
            'formatter': 'standard',
        },
        'email': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/email.log"),
            'formatter': 'standard',
        },
        'jobslog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/jobs.log"),
            'formatter': 'standard',
        },
        "post_office": {
            "level": "DEBUG",
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/postoffice.log"),
            "formatter": "post_office"
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'payments': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/payments.log"),
            'formatter': 'standard',
        },

        # everything that goes to syslog goes to papertrail https://papertrailapp.com/systems/1848252051/events
        'SysLog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'standard',
            'address': ('logs6.papertrailapp.com', 34636)
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logfile','console','SysLog'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {
            'handlers': ['api', 'console', 'SysLog'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'calculations': {
            'handlers': ['calclog', 'console',],
            'level': 'DEBUG',
            'propagate': False,
        },
        'jobs': {
            'handlers': ['jobslog','console','SysLog'],
            'level': 'INFO',
            'propagate': True,
        },

        'contact': {
            'handlers': ['contactlog', ],
            'level': 'DEBUG',
            'propagate': True,
        },
        'email': {
            'handlers': ['email', ],
            'level': 'DEBUG',
            'propagate': True,
        },

        "post_office": {
            "handlers": ["post_office",],
            "level": "INFO"
        },
        "payments": {
            "handlers": ["payments","console"],
            "level": "INFO"
        },

        'javascript_error': {
            'handlers': [ 'logfile','console','SysLog'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.utils.autoreload': {
            'level': 'INFO',
        },
    },
}

STRIPE_PUBLIC_KEY = "sk_test_123"
STRIPE_SECRET_KEY = "sk_test_123"

# used in scheduling - duration in seconds
DEFAULT_SLOT_DURATION = 300

# set in wsgi.py - os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "config.google-creds.json")
#GOOGLE_CREDENTIALS_LOCATION = str(os.path.join(BASE_DIR, "config/google-creds.json"))
#os.environ.setdefault("GOOGLE_CREDENTIALS_LOCATION",str(os.path.join(BASE_DIR, "config/google-creds.json") ))
CLICKY_SITE_ID = '101062055'
CRAZY_EGG_ACCOUNT_NUMBER = '00672125'

BOT_LIST = ['63.143.42.247', '66.249.66.87']

NOTIFICATIONS = True   # write to news feed etc.

DEFAULT_NUM_DP = 2  # default number of decimal places if not specified in event or competition

LOCATION_FIELD = {
    'provider.google.api': '//maps.google.com/maps/api/js?sensor=false',
    'provider.google.api_key': 'AIzaSyDd11csXXOYNHTMQZ6n0xglFE-Bfbg_Z8M',
    'provider.google.api_libraries': '',
    'provider.google.map.type': 'ROADMAP',
}


#
#
# #RQ_QUEUES required by imagekit
# # if getting error re RQ_QUEUES not set then make sure django_rq is not installed
# # ENABLES for current master - Sep2020
# try:
#     from django_rq import job
# except ImportError:
#     pass
# else:
#     _rq_job = job('default', result_ttl=0)(_generate_file)
#
#
#
# #NOTE: Ensure REDIS_DB is used everywhere and no hard coding of db or just using default
# REDIS_DB = {
#     'DEFAULT': '0',
#     'SETTINGS': '1',
#     'SESSIONS': '2',
#     'CACHE': '3',
#     'SCHEDULER': '5',
#     'Q': '10',
# }
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int( os.getenv("REDIS_PORT", "6379") )
# #REDIS_PASSWORD = SECRET_REDIS_PASSWORD
# REDIS_DATABASE = REDIS_DB["DEFAULT"]
# REDIS_LOCATION="redis://%s:%s/%s" % (REDIS_HOST, REDIS_PORT, REDIS_DATABASE)
# #if REDIS_PASSWORD:
# #    REDIS_LOCATION=REDIS_LOCATION.replace('redis://','redis://:%s@' % REDIS_PASSWORD)
#
# REDIS_METRICS = {
#     'HOST': REDIS_HOST,
#     'PORT': REDIS_PORT,
#     'DB':  REDIS_DATABASE,
#     #'PASSWORD': REDIS_PASSWORD,
#     'SOCKET_TIMEOUT': None,
#     'SOCKET_CONNECTION_POOL': None,
#     'MIN_GRANULARITY': 'daily',
#     'MAX_GRANULARITY': 'yearly',
#     'MONDAY_FIRST_DAY_OF_WEEK': False,
# }
#
#
# #COLLECT_METRICS = _get_flag("COLLECT_METRICS", True)
# if not REDIS_DB:
#     raise RuntimeError("REDIS_DB not set; initialize redis before rq")
#
# # TODO: include redis password?
# _rq_redis_connection = { 'HOST': REDIS_HOST,
#                          'PORT': REDIS_PORT,
#                          'DB': REDIS_DB
#                          }
#
#
#
# RQ_QUEUES = {
#     'default': _rq_redis_connection,
#     'high': _rq_redis_connection,
#     'low': _rq_redis_connection,
# }
# print(RQ_QUEUES)
# # for rq dashboard
# RQ = { k.lower(): v for k,v in _rq_redis_connection.items() }
#



GOOGLE_CODE = ''
FACEBOOK_CODE='''

    '''
FACEBOOK_SHARE='''
 <!-- Load Facebook SDK for JavaScript -->
    <div id="fb-root"></div>
    <script>(function(d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s); js.id = id;
        js.src = "https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v3.0";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));</script>
'''
DATA_QUALITY_DEFAULTS = {
    "ARCHIVE_SCORESHEET" : 30,
}

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

