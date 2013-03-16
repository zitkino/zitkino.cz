# -*- coding: utf-8 -*-


import os
import logging
from urlparse import urlparse

from zitkino import __version__ as version


LOGGING = {
    'format': '[%(levelname)s] %(message)s',
    'level': logging.DEBUG,
}

mongodb_uri = urlparse(os.getenv('MONGOLAB_URI', 'mongodb://localhost:27017'))
MONGODB_SETTINGS = {
    'username': mongodb_uri.username,
    'password': mongodb_uri.password,
    'host': mongodb_uri.netloc,
    'port': mongodb_uri.port,
    'db': mongodb_uri.path.replace('/', '') or 'zitkino',
}

SEND_FILE_MAX_AGE_DEFAULT = 157680000  # 5 years in seconds

USER_AGENT = 'zitkino/{0} (+http://zitkino.cz)'.format(version)
GA_CODE = 'UA-1316071-11'
