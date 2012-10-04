# -*- coding: utf-8 -*-


__version__ = '0.1.dev1349338548'


import logging

from flask import Flask
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')


db = MongoEngine(app)


logging_level = logging.DEBUG if app.debug else logging.INFO
logging.basicConfig(level=logging_level, filename=app.config['LOG_FILE'])


from zitkino import models, views, templating
