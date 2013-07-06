# -*- coding: utf-8 -*-


import datetime
from decimal import Decimal
from HTMLParser import HTMLParser

import times


def price(value):
    """Decimal number factory with some initial value polishing."""
    value = unicode(value)
    value = value.replace(',', '.')
    value = value.replace(u'Kč', '')
    return Decimal(value.strip())


def date_time_year(date, time, year=None, tz='Europe/Prague'):
    """Parses strings representating parts of datetime and combines them
    together. Resulting datetime is in UTC.
    """
    dt_string = '{date} {time} {year}'.format(
        date=date,
        time=time,
        year=year or times.now().year,
    )
    possible_formats = (
        '%d. %m. %H:%M %Y',
        '%d.%m. %H:%M %Y',
        '%d. %m. %H.%M %Y',
        '%d.%m. %H.%M %Y',
    )
    for format in possible_formats:
        try:
            dt = datetime.datetime.strptime(dt_string, format)
        except ValueError:
            pass
        else:
            break
    return times.to_universal(dt, tz)


def month(m):
    """Takes month and returns it's numeric representation."""
    cs = (u'led', u'úno', u'bře', u'dub', u'kvě', u'čvn',
          u'čvc', u'srp', u'zář', u'říj', u'lis', u'pro')
    en = ('jan', 'feb', 'mar', 'apr', 'may', 'jun',
          'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
    m = m.lower()
    if m in cs:
        return cs.index(m)
    if m in en:
        return en.index(m)
    raise ValueError("Invalid month.")


def html_text(text):
    """Decodes all HTML entities back to Unicode characters."""
    return HTMLParser().unescape(text)
