# -*- coding: utf-8 -*-


import re

import requests
import unidecode

from . import app


def slugify(string, sep='-'):
    string = unidecode.unidecode(string).lower()
    string = re.sub(r'\W+', sep, string)
    return re.sub('{}+'.format(sep), sep, string).strip(sep)


def clean_whitespace(value):
    """Normalizes whitespace."""
    whitespace_re = re.compile(
        ur'[{0}\s\xa0]+'.format(
            re.escape(''.join(map(unichr, range(0, 32) + range(127, 160))))
        )
    )
    return whitespace_re.sub(' ', value).strip()


def download(url, method='get', **kwargs):
    """Requests wrapper."""
    kwargs.setdefault('timeout', app.config['HTTP_TIMEOUT'])

    headers = kwargs.get('headers', {})
    headers.setdefault('User-Agent', app.config['USER_AGENT'])

    req = getattr(requests, method)
    resp = req(url, **kwargs)

    resp.raise_for_status()
    return resp
