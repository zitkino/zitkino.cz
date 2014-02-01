# -*- coding: utf-8 -*-


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

    def request(self, method, url, **kwargs):
        log.debug('HTTP: %s %s', method.upper(), urlparse(url).netloc)
        try:
            # set default timeout
            kwargs.setdefault('timeout', app.config['HTTP_TIMEOUT'])

            # by default we don't verify certificates
            kwargs.setdefault('verify', False)
            resp = super(Session, self).request(method, url, **kwargs)

            # implicit exception raising on HTTP errors, can be turned
            # off ad-hoc by extra raise_for_status=False keyword argument
            if kwargs.get('raise_for_status', True):
                resp.raise_for_status()
            return resp

        except requests.exceptions.ConnectionError as e:
            if 'Connection refused' in unicode(e):
                raise Banned
            raise


from requests.exceptions import *  # NOQA
