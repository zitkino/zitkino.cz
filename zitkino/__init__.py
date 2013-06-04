# -*- coding: utf-8 -*-


__version__ = '2.0.9'


import logging

from flask import Flask
from flask.ext.gzip import Gzip

from .mongo import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')
logging.basicConfig(**app.config['LOGGING'])


Gzip(app)


db = MongoEngine(app)


from zitkino import views, templating  # NOQA
