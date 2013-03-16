# -*- coding: utf-8 -*-


import re
from jinja2 import Markup
from flask.ext.gzip import Gzip
from flask import url_for as original_url_for

from zitkino import app, __version__ as version
from zitkino.utils import slugify


Gzip(app)


@app.context_processor
def redefine_url_for():
    def url_for(endpoint, **values):
        url = original_url_for(endpoint, **values)
        if endpoint in ['static', 'favicon']:
            sep = '&' if ('?' in url) else '?'
            url += '{0}v{1}'.format(sep, version)
        return url
    return {'url_for': url_for}


@app.template_filter()
def date(dt):
    d = dt.strftime('%d. %m.')
    return re.sub(r'0+(\d+)', r'\1', d)


app.template_filter()(slugify)


@app.template_filter()
def email(address):
    username, server = address.split('@')
    markup = ('<a href="mailto:{username}&#64;{server}">'
              '{username}&#64;<!---->{server}</a>').format(username=username,
                                                           server=server)
    return Markup(markup)
