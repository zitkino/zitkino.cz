# -*- coding: utf-8 -*-


__version__ = '2.0.0'


import logging
from flask import Flask


app = Flask(__name__)
app.config.from_object('zitkino.config')
logging.basicConfig(**app.config['LOGGING'])


from zitkino import views, templating
