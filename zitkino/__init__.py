# -*- coding: utf-8 -*-


from flask import Flask
from flask.ext.assets import Environment as Assets

from . import log
from .cache import Cache
from .mongo import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')
app.config.from_envvar('ZITKINO_CONFIG', silent=True)


log.init_app(app, **app.config['LOGGING'])


assets = Assets(app)
db = MongoEngine(app)
cache = Cache(app)


from . import views, templating  # NOQA
