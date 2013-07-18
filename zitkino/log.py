# -*- coding: utf-8 -*-


import sys
import logging
from functools import wraps

from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler


def init_app(app, *args, **kwargs):
    logging.basicConfig(*args, **kwargs)

    sentry = Sentry(app)
    handler = SentryHandler(sentry.client, level=logging.ERROR)
    logging.getLogger().addHandler(handler)


debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical
exception = logging.exception


def scraper(msg, *args, **kwargs):
    info('Scraper: ' + msg, *args, **kwargs)


def showtime(showtime):
    info(
        u'Showtime: %s | %s | %s',
        showtime.starts_at,
        showtime.cinema.name,
        showtime.film.title_main
    )


def log_exceptions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            exc_info = sys.exc_info()
            exception(
                '%s: %s',
                exc_info[0].__name__,
                exc_info[1],
                exc_info=exc_info
            )
            raise
    return wrapper
