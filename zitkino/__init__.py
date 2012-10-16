# -*- coding: utf-8 -*-


__version__ = '0.1.dev1350420207'


import logging
from flask import Flask
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')


logging_level = logging.DEBUG if app.debug else logging.INFO
logging_format = '[%(levelname)s] %(name)s %(message)s'
logging.basicConfig(format=logging_format, level=logging_level)


db = MongoEngine(app)


from zitkino import models, views, templating
