# -*- coding: utf-8 -*-


import datetime
from decimal import Decimal

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
        '%d. %m. %H.%M %Y',
    )
    for format in possible_formats:
        try:
            dt = datetime.datetime.strptime(dt_string, format)
        except ValueError:
            pass
        else:
            break
    return times.to_universal(dt, tz)
