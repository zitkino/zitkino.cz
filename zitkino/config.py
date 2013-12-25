# -*- coding: utf-8 -*-


import os
import base64
import logging
from urlparse import urlparse


DEBUG = bool(os.getenv('ZITKINO_DEBUG', False))
SENTRY_DSN = os.getenv('SENTRY_DSN')


### Logging

LOGGING = {
    'format': '[%(levelname)s] %(message)s',
    'level': logging.DEBUG,
}


### Database

mongodb_uri = urlparse(os.getenv('MONGOLAB_URI', 'mongodb://localhost:27017'))

MONGODB_USERNAME = mongodb_uri.username
MONGODB_PASSWORD = mongodb_uri.password
MONGODB_HOST = mongodb_uri.hostname
MONGODB_PORT = mongodb_uri.port
MONGODB_DB = mongodb_uri.path.replace('/', '') or 'zitkino'


### Static files

ASSETS_DEBUG = DEBUG
ASSETS_AUTO_BUILD = DEBUG
ASSETS_SASS_DEBUG_INFO = DEBUG

SEND_FILE_MAX_AGE_DEFAULT = 157680000  # 5 years in seconds


### Caching

CACHE_DEFAULT_TIMEOUT = 86400
CACHE_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..', 'tmp')
)


### Templates

GA_CODE = 'UA-1316071-11'


### Scraping

USER_AGENT = 'zitkino/1.0 (+http://zitkino.cz)'
HTTP_TIMEOUT = 10


### SynopsiTV credentials

# Encoding the password by base64 is not meant to be secure,
# it just prevents 'man-behind-my-shoulder' attacks.

SYNOPSITV_OAUTH_KEY = os.getenv('SYNOPSITV_OAUTH_KEY')
SYNOPSITV_OAUTH_SECRET = os.getenv('SYNOPSITV_OAUTH_SECRET')
SYNOPSITV_USERNAME = os.getenv('SYNOPSITV_USERNAME')

password = os.getenv('SYNOPSITV_PASSWORD')
SYNOPSITV_PASSWORD = base64.b64decode(password) if password else None
