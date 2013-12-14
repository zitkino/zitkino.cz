# -*- coding: utf-8 -*-


from flask import Flask
from flask.ext.assets import Environment as Assets

from . import log
from .mongo import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')
app.config.from_envvar('ZITKINO_CONFIG', silent=True)

log.init_app(app, **app.config['LOGGING'])


assets = Assets(app)
db = MongoEngine(app)


from zitkino import views, templating  # NOQA
