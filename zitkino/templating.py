# -*- coding: utf-8 -*-


import re
import urllib
import datetime

import times
from jinja2 import Markup

from . import app
from .utils import slugify


@app.template_filter()
def date(value, relative=True):
    """Simple, human-readable date."""
    date = value.date() if isinstance(value, datetime.datetime) else value
    today = times.to_local(times.now(), 'Europe/Prague').date()

    if relative:
        if today == date:
            return u'Dnes'
        if date - today == datetime.timedelta(days=1):
            return u'Zítra'

    date_str = value.strftime('%d. %m.')
    date_str = re.sub(r'0+(\d+)', r'\1', date_str)  # strip leading zeros

    weekdays = (u'pondělí', u'úterý', u'středa', u'čtvrtek',
                u'pátek', u'sobota', u'neděle')
    weekday_str = weekdays[value.weekday()].capitalize()

    result = u'{weekday} {date}'.format(weekday=weekday_str, date=date_str)
    result = result.replace(' ', u'\u00A0')  # no-break spaces
    return result


@app.template_filter()
def email(address):
    """Obfuscate e-mail address."""
    username, server = address.split('@')
    markup = ('<a href="mailto:{username}&#64;{server}">'
              '{username}&#64;<!---->{server}</a>').format(username=username,
                                                           server=server)
    return Markup(markup)


@app.template_filter()
def urlencode(value):
    """Encode string to be used in URL."""
    return urllib.quote(unicode(value).encode('utf8'))


@app.template_filter()
def unique(iterable, attribute=None):
    """Filters a sequence of objects by looking at either
    the object or the attribute and only selecting the unique ones.
    """
    if attribute:
        get_value = lambda obj: getattr(obj, attribute)
    else:
        get_value = lambda obj: obj

    values = set()
    for obj in iterable:
        original_len = len(values)
        values.add(get_value(obj))
        if original_len < len(values):
            yield obj


app.template_filter()(slugify)
