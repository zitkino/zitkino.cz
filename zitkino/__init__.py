# -*- coding: utf-8 -*-


__version__ = '0.1.dev1347232210'


from flask import Flask
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')


db = MongoEngine(app)


from zitkino import models, views
