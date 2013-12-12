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
def uppercase_first(value):
    return value[0].upper() + value[1:]


@app.template_filter()
def prettify_url(value):
    """Make given URL nice so it could be displayed to user."""
    return re.sub(r'^(https?://)?(www\.)?', '', value).rstrip('/')


@app.template_filter()
def map_link_url(name=None, coords=None):
    """Construct link to maps."""
    q = ''
    if coords:
        q += '{},{}'.format(*coords)
        if name:
            q += ' '
    if name:
        q += '({})'.format(name)
    return 'https://maps.google.com/maps?q={}&hl=cs'.format(urlencode(q))


@app.template_filter()
def map_image_url(coords):
    return (
        'https://maps.googleapis.com/maps/api/staticmap'
        '?zoom=15'
        '&size=300x300'
        '&maptype=roadmap'
        '&markers=color:0xEB2D2E%7C{},{}'
        '&sensor=false'
        '&visual_refresh=true'
        '&language=cs'
        '&scale=2'
    ).format(*coords)


@app.template_filter()
def film_length(minutes):
    hours, minutes = divmod(minutes, 60)
    if hours:
        return '{}h {}m'.format(hours, minutes)
    return '{}m'.format(minutes)


@app.template_filter()
def film_rating_icon_class(rating):
    if rating >= 85:
        return 'fa-star'
    if 85 > rating >= 65:
        return 'fa-star-half-o'
    return 'fa-star-o'


@app.template_filter()
def film_ratings(ratings):
    return u', '.join([
        u'{}: {} %'.format(name, int(value))
        for (name, value) in ratings.items()
    ])


app.template_filter()(slugify)
