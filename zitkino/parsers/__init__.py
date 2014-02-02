# -*- coding: utf-8 -*-


import re
import datetime
from decimal import Decimal

import times
from icalendar import Calendar

from .html import html  # NOQA
from ..utils import clean_whitespace


def ical(text):
    """Takes text and returns iCalendar data structure."""
    return Calendar.from_ical(text)


def price(value):
    """Decimal number factory with some initial value polishing."""
    value = unicode(value)
    value = value.replace(',', '.')
    value = value.replace(u'Kč', '')
    return Decimal(value.strip())


def date_time_year(date, time, year=None, tz='Europe/Prague'):
    """Parses strings representing parts of datetime and combines them
    together. Resulting datetime is in UTC.
    """
    dt_string = u'{date} {time} {year}'.format(
        date=date,
        time=time,
        year=year or times.now().year,
    )
    possible_formats = (
        '%d. %m. %H:%M %Y',
        '%d. %m. %H.%M %Y',
    )
    dt = None
    for format in possible_formats:
        try:
            dt = datetime.datetime.strptime(dt_string, format)
        except ValueError:
            pass
        else:
            break
    if dt:
        return times.to_universal(dt, tz)
    else:
        raise ValueError(dt_string)


def date_cs(value):
    """Parses a Czech text to a date object."""
    value = clean_whitespace(value)
    match = re.search(r'(\d+)\s*\.?\s*(\w+)(\s+\d{2,4})?', value, re.U)
    if match:
        # day
        day = int(match.group(1))

        # month
        try:
            month = int(match.group(2))
        except ValueError:
            months = (
                u'leden', u'únor', u'březen', u'duben',
                u'květen', u'červen', u'červenec', u'srpen',
                u'září', u'říjen', u'listopad', u'prosinec',
                u'ledna', u'února', u'března', u'dubna',
                u'května', u'června', u'července', u'srpna',
                u'září', u'října', u'listopadu', u'prosince',
            )
            month = (months.index(match.group(2)) % 12) + 1

        # year
        if not match.group(3):
            year = times.now().year
        elif len(match.group(3)) == 2:
            year = 2000 + int(match.group(3))
        else:
            year = int(match.group(3))

        return datetime.date(year, month, day)
    return None


def resize(resize):
    if resize:
        width, height = resize.split('x')
        if width and height:
            return (int(width), int(height))
    return None


def youtube_url(url):
    if 'youtube' in url:
        if 'embed' in url:
            return 'https://www.youtube.com/watch?v={}'.format(
                re.search(r'embed/([^\?]+)', url).group(1)
            )
        raise NotImplementedError
    raise ValueError
