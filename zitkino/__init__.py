# -*- coding: utf-8 -*-


__version__ = '0.1.dev1349339677'


from flask import Flask
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')


db = MongoEngine(app)


from zitkino import logging_utils, models, views, templating


logging_utils.init_app(app)
