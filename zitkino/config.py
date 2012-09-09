# -*- coding: utf-8 -*-


import urlparse
from os import environ


mongolab_uri = environ.get('MONGOLAB_URI')
url = urlparse.urlparse(mongolab_uri)

MONGODB_USERNAME = url.username
MONGODB_PASSWORD = url.password
MONGODB_HOST = url.hostname or 'localhost'
MONGODB_PORT = url.port or 27017
MONGODB_DB = url.path[1:]
