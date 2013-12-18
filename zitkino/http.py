# -*- coding: utf-8 -*-


import re
import time
import random
from urlparse import urlparse

import requests

from . import app
from . import log


class Banned(requests.ConnectionError):

    def __init__(self):
        super(Banned, self).__init__('The connection was refused.')


class Session(requests.Session):

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.headers['User-Agent'] = app.config['USER_AGENT']

    def request(self, method, url, *args, **kwargs):
        log.debug('HTTP: %s %s', method.upper(), urlparse(url).netloc)
        try:
            # set default timeout
            kwargs.setdefault('timeout', app.config['HTTP_TIMEOUT'])

            # by default we don't verify certificates
            kwargs.setdefault('verify', False)
            resp = super(Session, self).request(method, url, *args, **kwargs)

            # implicit exception raising on HTTP errors, can be turned
            # off ad-hoc by extra raise_for_status=False keyword argument
            if kwargs.get('raise_for_status', True):
                resp.raise_for_status()
            return resp

        except requests.ConnectionError as e:
            if 'Connection refused' in unicode(e):
                raise Banned
            raise


class CsfdSession(Session):
    """Deals with various ČSFD's network issues and eventually
    tries to perform the same requests again.
    """

    def wait(self):
        seconds = random.randrange(1, 5, 1)
        log.debug('HTTP: Waiting for %d seconds.', seconds)
        time.sleep(seconds)

    def request(self, *args, **kwargs):
        try:
            self.wait()
            return super(CsfdSession, self).request(*args, **kwargs)

        except requests.TooManyRedirects:
            return self.request(*args, **kwargs)
        except requests.HTTPError as e:
            if e.response.status_code in (502, 403):
                return self.request(*args, **kwargs)
            raise


class SynopsitvSession(Session):
    """Deals with various SynopsiTV's network issues and eventually
    tries to perform the same requests again.
    """

    def request(self, *args, **kwargs):
        try:
            return super(SynopsitvSession, self).request(*args, **kwargs)
        except requests.SSLError:
            return self.request(*args, **kwargs)


session_map = (
    (re.compile(r'^https?://(www\.)?csfd\.cz'), CsfdSession),
    (re.compile(r'^https?://api\.synopsi\.tv'), SynopsitvSession),
)


def request(method, url, **kwargs):
    session_cls = Session

    for pattern, cls in session_map:
        if pattern.search(url):
            session_cls = cls
            break

    session = session_cls()
    return session.request(method=method, url=url, **kwargs)


def get(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('get', url, **kwargs)


def options(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('options', url, **kwargs)


def head(url, **kwargs):
    kwargs.setdefault('allow_redirects', False)
    return request('head', url, **kwargs)


def post(url, data=None, **kwargs):
    return request('post', url, data=data, **kwargs)


def put(url, data=None, **kwargs):
    return request('put', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('patch', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('delete', url, **kwargs)


from requests.exceptions import *  # NOQA
