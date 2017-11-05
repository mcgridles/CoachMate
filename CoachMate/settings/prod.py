# Production Settings
import os

from base import *

DEBUG=False

ALLOWED_HOSTS += 'coachmate.herokuapp.com'

DATABASES = {
    'default': dj_database_url.config()
}

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

STATICFILES_STORAGE = 'CoachMate.custom_storages.StaticStorage'
DEFAULT_FILE_STORAGE = 'CoachMate.custom_storages.MediaStorage'
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['S3_BUCKET_NAME']
AWS_HEADERS = {'Cache-Control': 'max-age=86400',}
AWS_S3_HOST = 's3.us-east-2.amazonaws.com'
AWS_QUERYSTRING_AUTH = False

# Production security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CONN_MAX_AGE = 3600
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True # [1]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
