# -*- coding: utf-8 -*-


__version__ = '0.1.dev1347189047'


from flask import Flask
from flask.ext.mongoalchemy import MongoAlchemy


app = Flask(__name__)
app.config.from_object('zitkino.config')


db = MongoAlchemy(app)


import views
