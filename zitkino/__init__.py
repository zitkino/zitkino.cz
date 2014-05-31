# -*- coding: utf-8 -*-


import os
import re

from flask import Flask
from flask.ext.assets import Environment as Assets

from . import log, parsers
from .mongo import MongoEngine


app = Flask(__name__)
app.config.from_object('zitkino.config')
app.config.from_envvar('ZITKINO_CONFIG', silent=True)


log.init_app(app, **app.config['LOGGING'])


if not 'POSTER_SIZES' in app.config:
    def _scan_templates_for_poster_sizes(app):
        path = os.path.join(app.root_path, app.template_folder)
        size_re = re.compile(r"url_for\('poster'[^\d\)]+(\d+x\d+)")
        sizes = []

        templates = []
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith('.html'):
                    templates.append(os.path.join(root, filename))

        for template in templates:
            with open(template) as f:
                for line in f:  # not bulletproof, but fast & good enough
                    sizes.extend(m.group(1) for m in size_re.finditer(line))

        return [parsers.size(size) for size in frozenset(sizes)]

    app.config['POSTER_SIZES'] = _scan_templates_for_poster_sizes(app)


assets = Assets(app)
db = MongoEngine(app)


from . import views, templating  # NOQA
