# -*- coding: utf-8 -*-


import re

from jinja2 import Markup

from . import app
from .utils import slugify


@app.template_filter()
def date(dt):
    """Simple, human-readable date."""
    d = dt.strftime('%d. %m.')
    return re.sub(r'0+(\d+)', r'\1', d)


@app.template_filter()
def email(address):
    """Obfuscate e-mail address."""
    username, server = address.split('@')
    markup = ('<a href="mailto:{username}&#64;{server}">'
              '{username}&#64;<!---->{server}</a>').format(username=username,
                                                           server=server)
    return Markup(markup)


@app.template_filter()
def uppercase_first(text):
    return text[0].upper() + text[1:]


app.template_filter()(slugify)
