# -*- coding: utf-8 -*-


import re
import logging
import unidecode
from functools import wraps


def slugify(string, sep='_'):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', sep, string)


def deflate_exceptions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
    return wrapper
