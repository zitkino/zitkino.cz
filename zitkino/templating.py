# -*- coding: utf-8 -*-


import urllib
from jinja2 import Markup

from zitkino import app


@app.template_filter('urlencode')
def urlencode_filter(s):
    if isinstance(s, Markup):
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)


@app.template_filter('format_date')
def format_date_filter(dt):
    day = dt.strftime('%d').lstrip('0')
    month = dt.strftime('%m').lstrip('0')
    return '{d}. {m}.'.format(d=day, m=month)


@app.template_filter('format_date_ics')
def format_date_ics_filter(dt):
    return dt.strftime('%Y%m%d')


@app.template_filter('format_timestamp_ics')
def format_timestamp_ics_filter(dt):
    return dt.strftime('%Y%m%dT%H%M%SZ')
