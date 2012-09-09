# -*- coding: utf-8 -*-


__version__ = '0.1.dev1347189047'


from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('zitkino.config')


db = SQLAlchemy(app)


import views
