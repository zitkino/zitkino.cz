# -*- coding: utf-8 -*-


import os
from flask import render_template, send_from_directory

from zitkino import app


@app.context_processor
def inject_config():
    return {'ga_code': app.config['GA_CODE'],
            'debug': app.debug}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')
