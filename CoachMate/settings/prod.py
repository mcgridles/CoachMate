# Production Settings

from base import *

DEBUG=False

ALLOWED_HOSTS += 'www.example.com'

DATABASES = {
    'default': dj_database_url.config()
}

STATICFILES_LOCATION = 'static'
MEDIAFILES_LOCATION = 'media'

# Production security settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CONN_MAX_AGE = 3600
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True # [1]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
