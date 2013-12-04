# -*- coding: utf-8 -*-


import re
import json

import requests

from zitkino import app
from zitkino.models import Film

from .imdb import ImdbFilmID
from . import BaseFilmID, BaseFilmService


class SynopsitvFilmID(BaseFilmID):
    url_re = re.compile(r'/(tv-shows|movies)/([^/]+)')
    url_re_group = 2


class SynopsitvFilmService(BaseFilmService):

    name = u'SynopsiTV'
    url_attr = 'url_synopsitv'

    oauth_key = app.config['SYNOPSITV_OAUTH_KEY']
    oauth_secret = app.config['SYNOPSITV_OAUTH_SECRET']
    username = app.config['SYNOPSITV_USERNAME']
    password = app.config['SYNOPSITV_PASSWORD']

    properties = [
        'id', 'cover_large', 'url', 'name', 'year', 'trailer',
        'directors', 'runtime',
    ]

    def __init__(self):
        self.token = self._get_token()

    def _get_token(self):
        resp = requests.post(
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
        resp.raise_for_status()
        return json.loads(resp.content)['access_token']

    def search(self, titles, year=None):
        for title in titles:
            resp = requests.get(
                'https://api.synopsi.tv/1.0/title/identify/',
                params={
                    'bearer_token': self.token,
                    'file_name': title,
                    'year': year,
                    'title_property[]': ','.join(self.properties),
                },
            )
            if resp.status_code == 200:
                results = json.loads(resp.content)['relevant_results']
                if results:
                    return self._create_film(results[0])
        return None

    def lookup(self, url):
        title_id = SynopsitvFilmID.from_url(url)
        resp = requests.get(
            'https://api.synopsi.tv/1.0/title/{}/'.format(title_id),
            params={
                'bearer_token': self.token,
                'title_property[]': ','.join(self.properties),
            },
        )
        if resp.status_code == 404:
            return None
        return self._create_film(json.loads(resp.content))

    def lookup_obj(self, film):
        if not film.url_synopsitv and film.url_imdb:
            imdb_id = ImdbFilmID.from_url(film.url_imdb)
            resp = requests.get(
                'https://api.synopsi.tv/1.0/title/identify/',
                params={
                    'bearer_token': self.token,
                    'imdb_id': imdb_id,
                    'title_property[]': ','.join(self.properties),
                },
            )
            if resp.status_code == 200:
                results = json.loads(resp.content)['relevant_results']
                if results:
                    return self._create_film(results[0])
        return super(SynopsitvFilmService, self).lookup_obj(film)

    def _create_film(self, result):
        return Film(
            url_synopsitv='http://www.synopsi.tv' + result['url'],
            year=result.get('year'),
            title_main=result['name'],
            titles=[result['name']],
            directors=[d['name'] for d in result.get('directors', [])],
            length=result.get('runtime'),
            url_cover=result.get('cover_large'),
            url_trailer=result.get('trailer'),
        )


if __name__ == '__main__':
    print SynopsitvFilmService().search(['!'])
    print SynopsitvFilmService().search(['matrix'])
    print SynopsitvFilmService().lookup('http://synopsi.tv/movies/64978/the-matrix-1999/')
    print SynopsitvFilmService().lookup_obj(Film.objects.get(id='529c4729dd7ce9e34fc2d985'))
    print SynopsitvFilmService().lookup_obj(Film(url_imdb='http://imdb.com/title/tt0418832/'))
    print SynopsitvFilmService().lookup_obj(Film(titles=['Lie with me']))
