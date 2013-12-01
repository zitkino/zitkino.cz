# -*- coding: utf-8 -*-


import re
import urllib
from collections import namedtuple

from fuzzywuzzy import fuzz
from requests import HTTPError

from zitkino import parsers
from zitkino.models import Film
from zitkino.utils import download

from . import FilmDataService


FilmOrigin = namedtuple('FilmOrigin', ['year', 'length'])


class CSFDService(FilmDataService):

    name = u'ČSFD'
    url_attr = 'url_csfd'

    min_similarity_ratio = 90
    year_re = re.compile(r'(\d{4})')
    length_re = re.compile(r'(\d+)\s*min')
    id_re = re.compile(r'/film/(\d+)')  # /film/216106-lie-with-me/

    def _download(self, *args, **kwargs):
        try:
            return download(*args, **kwargs)
        except HTTPError as e:
            if e.response.status_code == 502:  # ČSFD's WTF issue, try again
                return self._download(*args, **kwargs)
            raise

    def search(self, titles, year=None):
        year = int(year) if year else None

        for title in titles:
            resp = self._download(
                'http://www.csfd.cz/hledat/complete-films/?q='
                + urllib.quote_plus(unicode(title).encode('utf-8'))
            )

            # direct redirect to the film page
            match = self.id_re.search(resp.url)
            if match:
                return self.lookup(resp.url)

            # results page
            html = parsers.html(resp.content, base_url=resp.url)
            results = self._iterparse_search_results(html, year)

            for result in results:
                similarity_ratio = fuzz.partial_ratio(
                    title,
                    self._parse_matched_title(result)
                )
                if similarity_ratio >= self.min_similarity_ratio:
                    return self.lookup(self._parse_film_url(result))

        return None  # there is no match

    def _iterparse_search_results(self, html, year=None):
        for result in html.cssselect('#search-films .content li'):
            if year:
                # check year
                year_el = result.cssselect_first('.film-year')
                if year_el:
                    year_text = year_el.text_content()
                else:
                    year_text = result.cssselect_first('p').text_content()
                if year != int(self.year_re.search(year_text).group(1)):
                    continue  # skip this result
            yield result

    def _parse_matched_title(self, result):
        title_el = result.cssselect_first('.search-name')
        if title_el is not None:
            return title_el.text_content().lstrip('(').rstrip(')')
        return result.cssselect('.film')[0].text_content()

    def _parse_film_url(self, result):
        result.make_links_absolute()
        return result.cssselect_first('.film').get('href')

    def lookup(self, url):
        try:
            resp = self._download(url)
        except HTTPError as e:
            if e.response.status_code == 404:
                return None  # there is no match
            raise

        html = parsers.html(resp.content, base_url=resp.url)
        info = html.cssselect_first('.content .info')

        titles = list(self._iterparse_titles(info))
        origin = self._parse_origin(info)

        return Film(
            url_csfd=resp.url,
            url_imdb=self._parse_imdb_url(html),
            title_main=titles[0],
            titles=titles,
            year=origin.year,
            directors=list(self._iterparse_directors(info)),
            length=origin.length,
            rating_csfd=self._parse_rating(html),
        )

    def _parse_imdb_url(self, html):
        imdb_img = html.cssselect_first('.links img.imdb')
        if imdb_img is not None:
            imdb_a = next(imdb_img.iterancestors(tag='a'))
            return imdb_a.get('href')
        return None

    def _iterparse_titles(self, info):
        yield info.cssselect_first('h1').text.strip()
        for title in info.cssselect('.names h3'):
            yield title.text.strip()

    def _parse_origin(self, info):
        year = length = None
        origin_text = info.cssselect_first('.origin').text.strip()
        for origin_fragment in origin_text.split(','):
            # year
            year_match = self.year_re.search(origin_fragment)
            if year_match:
                year = int(year_match.group(1))

            # length
            length_match = self.length_re.search(origin_fragment)
            if length_match:
                length = int(length_match.group(1))
        return FilmOrigin(year, length)

    def _iterparse_directors(self, info):
        for creators_h4 in info.cssselect('.creators div h4'):
            if u'Režie' in creators_h4.text_content():
                wrapper = next(creators_h4.iterancestors(tag='div'))
                for link in wrapper.cssselect('a'):
                    yield link.text_content()

    def _parse_rating(self, html):
        rating_text = html.cssselect_first('#rating h2').text_content()
        rating_text = rating_text.rstrip('%')
        if rating_text:
            return int(rating_text)
        return None
