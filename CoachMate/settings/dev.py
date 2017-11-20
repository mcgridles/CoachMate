# Development Settings

from .base import *

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['LOCAL_DATABASE_NAME'],
        'USER': os.environ['LOCAL_DATABASE_USER'],
        'PASSWORD': os.environ['LOCAL_DATABASE_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "home/static"),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
