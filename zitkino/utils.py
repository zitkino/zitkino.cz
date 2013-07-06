# -*- coding: utf-8 -*-


import re

import requests
import unidecode

from . import app


def slugify(string, sep='_'):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', sep, string).strip(sep)


def download(url, method='get', **kwargs):
    """Requests wrapper."""
    kwargs.setdefault('timeout', app.config['HTTP_TIMEOUT'])

    headers = kwargs.get('headers', {})
    headers.setdefault('User-Agent', app.config['USER_AGENT'])

    req = getattr(requests, method)
    resp = req(url, **kwargs)

    resp.raise_for_status()
    return resp
