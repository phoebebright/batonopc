import os

DEBUG = True

#set for DEMO mode
DEMO_MODE = True
DEMO_USER = "organiser@skor.ie"
DEMO_PASSWORD = "organiser"


#DC_MODE = True
#ROOT_URLCONF = 'config.urls_dc'

SECRET_KEY = "akQ3m*andfg.9MmEofgdyPDsYD32UWsx4"



DATABASES = {
    'default': {
        'ENGINE':  'django.db.backends.postgresql_psycopg2',
        'NAME': 'batonpc',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
}
}


WSGI_APPLICATION = None



ALLOWED_HOSTS = ['*',]

