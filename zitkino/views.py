# -*- coding: utf-8 -*-


import os

from flask import request, render_template, send_from_directory, url_for

from . import app, __version__


@app.context_processor
def inject_config():
    return {'config': app.config['GA_CODE'], 'debug': app.debug}


@app.context_processor
def redefine_url_for():
    """Enhancing original :func:`url_for` so it adds version to static
    files.
    """
    def url_for_static(endpoint, **values):
        if endpoint in ['static', 'static_files']:
            values['v'] = __version__
        return url_for(endpoint, **values)
    return {'url_for': url_for_static}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
@app.route('/apple-touch-icon.png')
@app.route('/robots.txt')
@app.route('/humans.txt')
def static_files():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, request.path.lstrip('/'))
