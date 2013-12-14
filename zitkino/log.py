# -*- coding: utf-8 -*-


import sys
import logging
from functools import wraps
from contextlib import contextmanager

from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler


def init_app(app, *args, **kwargs):
    logging.basicConfig(*args, **kwargs)

    sentry = Sentry(app)
    handler = SentryHandler(sentry.client, level=logging.ERROR)
    logging.getLogger().addHandler(handler)

    requests_log = logging.getLogger('requests')
    requests_log.setLevel(logging.WARNING)


debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical


def exception(**kwargs):
    exc_info = sys.exc_info()
    logging.exception(
        '%s: %s',
        exc_info[0].__name__,
        exc_info[1],
        exc_info=exc_info,
        **kwargs
    )


def log_exceptions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            exception()
            raise
    return wrapper


@contextmanager
def pass_on_exception():
    try:
        yield
    except Exception:
        exception()
