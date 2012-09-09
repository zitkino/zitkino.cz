# -*- coding: utf-8 -*-


import urlparse
from os import environ


mongolab_uri = environ.get('MONGOLAB_URI')
url = urlparse.urlparse(mongolab_uri)

MONGO_USERNAME = url.username
MONGO_PASSWORD = url.password
MONGO_HOST = url.hostname or 'localhost'
MONGO_PORT = url.port or 27017
MONGO_DBNAME = url.path[1:]
