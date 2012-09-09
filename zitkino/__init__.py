# -*- coding: utf-8 -*-


__version__ = '0.1.dev1347189019'


from flask import Flask
from flask_heroku import Heroku
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
heroku = Heroku(app)
db = SQLAlchemy(app)


@app.route('/')
def hello():
    return 'Hello!'
