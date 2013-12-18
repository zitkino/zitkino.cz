# -*- coding: utf-8 -*-


import re

from zitkino import http
from zitkino import parsers
from zitkino.models import Film

from . import BaseFilmID, BaseFilmService


class ImdbFilmID(BaseFilmID):
    url_re = re.compile(r'/title/tt([^/]+)')


class ImdbFilmService(BaseFilmService):

    name = u'IMDb'
    url_attr = 'url_imdb'

    year_re = re.compile(r'(\d{4})')

    def lookup(self, url):
        try:
            resp = self.session.get(url)
        except http.HTTPError as e:
            if e.response.status_code == 404:
                return None  # there is no match
            raise
        html = parsers.html(resp.content, base_url=resp.url)

        title = self._parse_title(html)
        return Film(
            url_imdb=resp.url,
            title_main=title,
            year=self._parse_year(html),
            rating_imdb=self._parse_rating(html),
        )

    def _parse_title(self, html):
        return html.cssselect_first('h1 [itemprop="name"]').text_content()

    def _parse_year(self, html):
        text = html.cssselect_first('h1 span.nobr').text_content()
        match = self.year_re.search(text)
        if match:
            return int(match.group(1))
        return None

    def _parse_rating(self, html):
        star = html.cssselect_first('.star-box-giga-star')
        if star is not None:
            return int(float(star.text_content().replace(',', '.')) * 10)
        return None
