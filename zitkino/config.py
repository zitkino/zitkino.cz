# -*- coding: utf-8 -*-


import urlparse
from os import environ


mongolab_uri = environ.get('MONGOLAB_URI')
url = urlparse.urlparse(mongolab_uri)

MONGOALCHEMY_USER = url.username
MONGOALCHEMY_PASSWORD = url.password
MONGOALCHEMY_SERVER = url.hostname
MONGOALCHEMY_PORT = url.port
MONGOALCHEMY_DATABASE = url.path[1:]
