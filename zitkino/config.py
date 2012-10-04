# -*- coding: utf-8 -*-


import urlparse
from os import environ


DEBUG = environ.get('ZITKINO_DEBUG', False)
LOG_FILE = environ.get('ZITKINO_LOG_FILE', None)


mongolab_uri = environ.get('MONGOLAB_URI')
url = urlparse.urlparse(mongolab_uri)

MONGODB_USERNAME = url.username
MONGODB_PASSWORD = url.password
MONGODB_HOST = url.hostname or 'localhost'
MONGODB_PORT = url.port or 27017
MONGODB_DB = url.path[1:]


USER_AGENT = 'zitkino/0.1.dev1349339677 (+http://zitkino.cz/)'
