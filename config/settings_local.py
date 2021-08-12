import os


#set for DC_MODE
DC_MODE = False

#set for DEMO mode
DEMO_MODE = True
DEMO_USER = "organiser@skor.ie"
DEMO_PASSWORD = "organiser"

GITHUB_TOKEN = "a3241854c19c261a87ec10f406e3d4f53ee83d9d"
GITHUB_REPO = "skorie/skorie"

#DC_MODE = True
#ROOT_URLCONF = 'config.urls_dc'

SECRET_KEY = "akQ3m*PoMWw27MWvZw648phPkZff.9MmEofgdyPDsYD32UWsx4"
SETUP = "DEV"
SITE_ID = 1
#SITE_URL = "http://127.0.0.1:8000"
#SITE_URL = "http://localhost:8003"     #<------ DC MODE
SITE_URL = "https://whinie.ngrok.io"
SITE_NAME = "Skor.ie (dev)"

#SKORIE_API = "https://skor.ie"
#SKORIE_API = "http://127.0.0.1:8000"
SKORIE_API = "https://whinie.ngrok.io"
SKORIE_EVENT_API = f"{SKORIE_API}/api/v2/"
SKORIE_RO_API =  f"{SKORIE_API}/api/g1/"
SKORIE_ENTER_API =  f"{SKORIE_API}/api/e1/"
TINYCLOUD_API_URL = "https://tinycloud.purit.ie"

HELPDESK_API = SKORIE_API
#SKORIE_API = "http://localhost:8003/dc"      #<------ DC MODE

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
#SECURE_SSL_REDIRECT = True

DEBUG=True
COMPRESS_ENABLED=False

#NOTE this does not work when running with settings_dc, have to go and change it there as well
USE_ASSETS = False   # use minified assets rather than individual javascript files - normally False for development

# AUTHENTICATION_BACKENDS = (
#
#     "django.contrib.auth.backends.ModelBackend",
#
#
# )

KEYCLOAK_USE_REALM = 'testclient'

HONEYCOMBE = False
HONEYCOMBE_KEY = "4270b75dfb48d992db9c283677d1ee43"


# INSTALLED_APPS += ('django_extensions',)

EMAIL_HOST = "mail.skor.ie"
EMAIL_PORT = os.getenv("EMAIL_PORT", "25")
EMAIL_HOST_USER = "info@skor.ie"
EMAIL_HOST_PASSWORD = "#Sbo955l"

#INSTALLED_APPS.append('debug_toolbar',)
# INSTALLED_APPS.append('silk',)
#MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware',)
#MIDDLEWARE.append( 'silk.middleware.SilkyMiddleware',)
DATABASES = {
    'default': {
        # 'ENGINE':  'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'skorie4',
        # 'USER': '',
        # 'PASSWORD': '',
        # 'HOST': 'localhost',
        # 'PORT': '',



        # 'ENGINE':  'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'skorie4',
        # 'USER': '',
        # 'PASSWORD': '',
        # 'HOST': 'localhost',
        # 'PORT': '',


    #
    #     'ENGINE':  'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'skorie_v2',
    #     'USER': 'doadmin',
    #     'PASSWORD': 'fqcxtkqglktdj7m0',
    #     'HOST': 'skorie1-do-user-2420134-0.db.ondigitalocean.com',
    #     'PORT': '25060',
    #     'CONN_MAX_AGE': None,
    # },


    # demo: Gives this error django_keycloak.models.Realm.client.RelatedObjectDoesNotExist: Realm has no client.
            'ENGINE':  'django.db.backends.postgresql_psycopg2',
        'NAME': 'skorie_demo_oct',
        'USER': 'skoriedemo',
        'PASSWORD': 'pZd62xucahuR-Y4pY',
        'HOST': 'skorie1-do-user-2420134-0.db.ondigitalocean.com',
        'PORT': '25060',
        'CONN_MAX_AGE': None,
    },
    # 'helpdesk': {
    #             'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #             # 'NAME': 'skorie3',
    #             'NAME': 'skoriehelp',
    #             # 'NAME': 'skorie_master',
    #             'USER': 'doadmin',
    #             'PASSWORD': 'fqcxtkqglktdj7m0',
    #             'HOST': 'skorie1-do-user-2420134-0.db.ondigitalocean.com',
    #             'PORT': '25060',
    # }
    #
    #         },
    # 'whinie': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'whinie',
    #     'USER': 'doadmin',
    #     'PASSWORD': 'fqcxtkqglktdj7m0',
    #     'HOST': 'skorie1-do-user-2420134-0.db.ondigitalocean.com',
    #     'PORT': '25060',
    # }
    # 'testsheets': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #      'NAME': 'skorie_master',
    #     'USER': 'doadmin',
    #     'PASSWORD': 'fqcxtkqglktdj7m0',
    #     'HOST': 'skorie1-do-user-2420134-0.db.ondigitalocean.com',
    #     'PORT': '25060',
    #
  #
  # }
}


WSGI_APPLICATION = None





ALLOWED_HOSTS = ['*',]


TEMPLATES = [

        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates'),
                     os.path.join(BASE_DIR, 'templates/organiser'),
                     os.path.join(BASE_DIR, 'templates/competitor'),
                     os.path.join(BASE_DIR, 'templates/video'),
                     ],
            'APP_DIRS': True,
            'OPTIONS': {
                'debug': DEBUG,
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'web.context_processors.include_settings',
                ],
            },
        },
]



CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}



EMAIL_PORT = 1025
EMAIL_HOST='localhost'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

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
        'contactlog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/contact.log"),
            'formatter': 'standard',
        },
        'testsheets': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 50,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, "logs/testsheets.log"),
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
        "post_office": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "post_office"
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
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
            "handlers": [ "console",],
            "level": "DEBUG"
        },
        "testsheets": {
            "handlers": ["console", ],
            "level": "DEBUG"
        },
        'django.utils.autoreload': {
            'level': 'INFO',
        },
    },
}


SOCIALACCOUNT_PROVIDERS = {
    'whinie_oa2': {
        'PROVIDER_URL': 'https://whin.ie/o/'
    },

}
WHINIE_CLIENT_ID = "wXaeVM1sDDQpNfxSuQ883gJgcPHhHVtmxKvLaT49"
WHINIE_API = "https://whin.ie"

STRIPE_ACTIVE = False
STRIPE_LIVE_PUBLIC_KEY = os.environ.get("STRIPE_LIVE_PUBLIC_KEY", "<your publishable key>")
STRIPE_LIVE_SECRET_KEY = os.environ.get("STRIPE_LIVE_SECRET_KEY", "<your secret key>")
STRIPE_TEST_PUBLIC_KEY = os.environ.get("STRIPE_TEST_PUBLIC_KEY", "pk_test_MOUEm8ShecQd9RdAB3fl8Cdx")
STRIPE_TEST_SECRET_KEY = os.environ.get("STRIPE_TEST_SECRET_KEY", "sk_test_2IVe0Jiii1yLc0pJkCelGwCD")
STRIPE_LIVE_MODE = False  # Change to True in production
DJSTRIPE_WEBHOOK_SECRET = "whsec_xxx"  # Get it from the section in the Stripe dashboard where you added the webhook endpoint

STRIPE_PUBLIC_KEY = STRIPE_TEST_PUBLIC_KEY
STRIPE_SECRET_KEY = STRIPE_TEST_SECRET_KEY

STRIPE_SUCCESS_URL = "https://cdc4a8b9.ngrok.io/pay/success/"
STRIPE_CANCEL_URL = "https://cdc4a8b9.ngrok.io/pay/cancel/"


STRIPE_CURRENCY = "EUR"

GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

GOOGLE_CODE =''

# SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
# SOCIAL_AUTH_AUTH0_DOMAIN = "whinie.eu.auth0.com"
# SOCIAL_AUTH_AUTH0_KEY = 'zLzl121JFC9MFyh5TysuNT51b55Cgz2w'
# SOCIAL_AUTH_AUTH0_SECRET = 'n_53LxCVSAxvYMz10dxT-jKhxsi0rAV1xufz0yY89nGlGvMmjvuMWQ6DXn-1pTdG'
#
# SOCIAL_AUTH_AUTH0_SCOPE = [
#     'openid',
#     'profile',
#     'email'
# ]


#RQ_QUEUES required by imagekit
# if getting error re RQ_QUEUES not set then make sure django_rq is not installed
#              '''
#              try:
#                  from django_rq import job
#              except ImportError:
#                  pass
#              else:
#                  _rq_job = job('default', result_ttl=0)(_generate_file)
#
#              '''



#NOTE: Ensure REDIS_DB is used everywhere and no hard coding of db or just using default
REDIS_DB = {
    'DEFAULT': '0',
    'SETTINGS': '1',
    'SESSIONS': '2',
    'CACHE': '3',
    'SCHEDULER': '5',
    'Q': '10',
}
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int( os.getenv("REDIS_PORT", "6379") )
#REDIS_PASSWORD = SECRET_REDIS_PASSWORD
REDIS_DATABASE = REDIS_DB["DEFAULT"]
REDIS_LOCATION="redis://%s:%s/%s" % (REDIS_HOST, REDIS_PORT, REDIS_DATABASE)
#if REDIS_PASSWORD:
#    REDIS_LOCATION=REDIS_LOCATION.replace('redis://','redis://:%s@' % REDIS_PASSWORD)

REDIS_METRICS = {
    'HOST': REDIS_HOST,
    'PORT': REDIS_PORT,
    'DB':  REDIS_DATABASE,
    #'PASSWORD': REDIS_PASSWORD,
    'SOCKET_TIMEOUT': None,
    'SOCKET_CONNECTION_POOL': None,
    'MIN_GRANULARITY': 'daily',
    'MAX_GRANULARITY': 'yearly',
    'MONDAY_FIRST_DAY_OF_WEEK': False,
}


#COLLECT_METRICS = _get_flag("COLLECT_METRICS", True)
if not REDIS_DB:
    raise RuntimeError("REDIS_DB not set; initialize redis before rq")

# TODO: include redis password?
_rq_redis_connection = { 'HOST': REDIS_HOST,
                         'PORT': REDIS_PORT,
                         'DB': REDIS_DB
                         }



RQ_QUEUES = {
    'default': _rq_redis_connection,
    'high': _rq_redis_connection,
    'low': _rq_redis_connection,
}

# for rq dashboard
RQ = { k.lower(): v for k,v in _rq_redis_connection.items() }

