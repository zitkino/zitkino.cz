# -*- coding: utf-8 -*-


import re
import datetime
from decimal import Decimal

import times


def price(value):
    """Decimal number factory with some initial value polishing."""
    value = unicode(value)
    value = value.replace(',', '.')
    value = value.replace(u'Kč', '')
    return Decimal(value.strip())


def whitespace(value):
    """Normalizes whitespace."""
    whitespace_re = re.compile(
        ur'[{0}\s\xa0]+'.format(re.escape(
        ''.join(map(unichr, range(0, 32) + range(127, 160)))))
    )
    return whitespace_re.sub(' ', value).strip()


def date_time_year(date, time, year=None, tz='Europe/Prague'):
    """Parses strings representating parts of datetime and combines them
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
