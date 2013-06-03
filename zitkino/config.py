# -*- coding: utf-8 -*-


import os
import logging
from urlparse import urlparse

from . import __version__ as version


### Logging ###

LOGGING = {
    'format': '[%(levelname)s] %(message)s',
    'level': logging.DEBUG,
}


### Database ###

mongodb_uri = urlparse(os.getenv('MONGOLAB_URI', 'mongodb://localhost:27017'))

MONGODB_USERNAME = mongodb_uri.username
MONGODB_PASSWORD = mongodb_uri.password
MONGODB_HOST = mongodb_uri.hostname
MONGODB_PORT = mongodb_uri.port
MONGODB_DB = mongodb_uri.path.replace('/', '') or 'zitkino'


### Static files ###

SEND_FILE_MAX_AGE_DEFAULT = 157680000  # 5 years in seconds


### Identification, codes, ... ###

USER_AGENT = 'zitkino/{0} (+http://zitkino.cz)'.format(version)
GA_CODE = 'UA-1316071-11'
