# -*- coding: utf-8 -*-


import re
import json

from zitkino import app
from zitkino import log
from zitkino import http
from zitkino.models import Film

from .imdb import ImdbFilmID
from . import BaseFilmID, BaseFilmService


class SynopsitvFilmID(BaseFilmID):
    url_re = re.compile(r'/(tv-shows|movies)/([^/]+)')
    url_re_group = 2


class SynopsitvSession(http.Session):
    """Deals with various SynopsiTV's network issues and eventually
    tries to perform the same requests again.
    """

    def request(self, *args, **kwargs):
        try:
            return super(SynopsitvSession, self).request(*args, **kwargs)
        except http.SSLError:
            log.debug('HTTP: SSL error. Retrying.')
            return self.request(*args, **kwargs)


class SynopsitvFilmService(BaseFilmService):

    name = u'SynopsiTV'
    url_attr = 'url_synopsitv'
    session_cls = SynopsitvSession

    oauth_key = app.config['SYNOPSITV_OAUTH_KEY']
    oauth_secret = app.config['SYNOPSITV_OAUTH_SECRET']
    username = app.config['SYNOPSITV_USERNAME']
    password = app.config['SYNOPSITV_PASSWORD']

    properties = [
        'id', 'cover_full', 'url', 'name', 'year', 'trailer',
        'directors', 'runtime',
    ]

    def __init__(self):
        self.__token = None
        super(SynopsitvFilmService, self).__init__()

    @property
    def _token(self):
        """Lazy token getter."""
        if not self.__token:
            resp = self.session.post(
                'https://api.synopsi.tv/oauth2/token/',
                data={
                    'grant_type': 'password',
                    'client_id': self.oauth_key,
                    'client_secret': self.oauth_secret,
                    'username': self.username,
                    'password': self.password,
                },
                auth=(self.oauth_key, self.oauth_secret)
            )
            self.__token = json.loads(resp.content)['access_token']
        return self.__token

    def _decode_results(self, response):
        # fix SynopsiTV's bug with double backslashes in some special unicode
        # characters
        content = re.sub(r'\\(\\u\d+)', r'\1', response.content)

        # return decoded JSON
        return json.loads(content)

    def search(self, titles, year=None):
        for title in titles:
            try:
                resp = self.session.get(
                    'https://api.synopsi.tv/1.0/title/identify/',
                    params={
                        'bearer_token': self._token,
                        'file_name': title,
                        'year': year,
                        'title_property[]': ','.join(self.properties),
                    },
                )
            except http.HTTPError as e:
                if e.response.status_code == 404:
                    continue
                raise

            results = self._decode_results(resp)['relevant_results']
            for result in results:
                if self._match_names(title, result['name']):
                    return self._create_film(result)
        return None

    def lookup(self, url):
        title_id = SynopsitvFilmID.from_url(url)

        try:
            resp = self.session.get(
                'https://api.synopsi.tv/1.0/title/{}/'.format(title_id),
                params={
                    'bearer_token': self._token,
                    'title_property[]': ','.join(self.properties),
                },
            )
        except http.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

        return self._create_film(self._decode_results(resp))

    def lookup_obj(self, film):
        if not getattr(film, 'url_synopsitv', None) and film.url_imdb:
            imdb_id = ImdbFilmID.from_url(film.url_imdb)

            try:
                resp = self.session.get(
                    'https://api.synopsi.tv/1.0/title/identify/',
                    params={
                        'bearer_token': self._token,
                        'imdb_id': imdb_id,
                        'title_property[]': ','.join(self.properties),
                    },
                )
            except http.HTTPError as e:
                if e.response.status_code != 404:
                    raise
            else:
                results = self._decode_results(resp)['relevant_results']
                if results:
                    return self._create_film(results[0])

        return super(SynopsitvFilmService, self).lookup_obj(film)

    def _create_film(self, result):
        if 'movie' not in result.get('cover_full', ''):
            url_poster = result.get('cover_full')
        else:
            url_poster = None  # default image

        return Film(
            url_synopsitv='http://www.synopsi.tv' + result['url'],
            year=result.get('year'),
            title_main=result['name'],
            directors=[d['name'] for d in result.get('directors', [])],
            length=result.get('runtime'),
            url_poster=url_poster,
            url_trailer=result.get('trailer') or None,
        )
