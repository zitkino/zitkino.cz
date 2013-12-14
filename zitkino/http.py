# -*- coding: utf-8 -*-


import re

import requests

from . import app


class Banned(requests.ConnectionError):

    def __init__(self):
        super(Banned, self).__init__('The connection was refused.')


class Session(requests.Session):

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)
        self.headers['User-Agent'] = app.config['USER_AGENT']

    def request(self, *args, **kwargs):
        # set default timeout
        kwargs.setdefault('timeout', app.config['HTTP_TIMEOUT'])

        # by default we don't verify certificates
        kwargs.setdefault('verify', False)
        resp = super(Session, self).request(*args, **kwargs)

        # implicit exception raising on HTTP errors, can be turned off ad-hoc
        # by extra raise_for_status=False keyword argument
        if kwargs.get('raise_for_status', True):
            resp.raise_for_status()
        return resp


class CsfdSession(Session):
    """Dealing with various ČSFD's network issues and eventually
    trying to perform requests again.
    """

    def request(self, *args, **kwargs):
        try:
            return super(CsfdSession, self).request(*args, **kwargs)

        except requests.TooManyRedirects:
            return self.request(*args, **kwargs)
        except requests.HTTPError as e:
            if e.response.status_code in (502, 403):
                return self.request(*args, **kwargs)
            raise
        except requests.ConnectionError as e:
            if 'Connection refused' in unicode(e):
                raise Banned
            raise


session_map = (
    (re.compile(r'^https?://([^\.]+\.)?csfd\.cz'), CsfdSession),
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
