# -*- coding: utf-8 -*-


import os

from flask import request, render_template, send_from_directory

from . import app
from .models import Showtime


@app.context_processor
def inject_config():
    return {'ga_code': app.config['GA_CODE'], 'debug': app.debug}


@app.route('/')
def index():
    showtimes = Showtime.upcoming()
    return render_template('index.html', showtimes=showtimes)


@app.route('/favicon.ico')
@app.route('/apple-touch-icon.png')
@app.route('/robots.txt')
@app.route('/humans.txt')
def static_files():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, request.path.lstrip('/'))
