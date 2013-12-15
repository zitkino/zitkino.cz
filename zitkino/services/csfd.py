# -*- coding: utf-8 -*-


import re
import urllib
import urlparse
from collections import namedtuple

from zitkino import http
from zitkino import parsers
from zitkino.models import Film

from . import BaseFilmID, BaseFilmService


class CsfdFilmID(BaseFilmID):
    url_re = re.compile(r'/film/(\d+)')


FilmOrigin = namedtuple('FilmOrigin', ['year', 'length'])


FilmTitles = namedtuple('FilmTitles', ['main', 'orig', 'others'])


class CsfdFilmService(BaseFilmService):

    name = u'ČSFD'
    url_attr = 'url_csfd'

    year_re = re.compile(r'(\d{4})')
    length_re = re.compile(r'(\d+)\s*min')

    def search(self, titles, year=None):
        year = int(year) if year else None

        for title in titles:
            resp = http.get(
                'http://www.csfd.cz/hledat/complete-films/?q='
                + urllib.quote_plus(unicode(title).encode('utf-8'))
            )

            # direct redirect to the film page
            try:
                CsfdFilmID.from_url(resp.url)
            except ValueError:
                pass
            else:
                return self.lookup(resp.url)

            # results page
            html = parsers.html(resp.content, base_url=resp.url)
            results = self._iterparse_search_results(html, year)

            for result in results:
                if self._match_names(title, self._parse_matched_title(result)):
                    return self.lookup(self._parse_film_url(result))

        return None  # there is no match

    def _iterparse_search_results(self, html, year=None):
        for result in html.cssselect('#search-films .content li'):
            if year:
                # check year
                year_el = result.cssselect_first('.film-year')

                if year_el is not None:
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
            resp = http.get(url)
        except http.HTTPError as e:
            if e.response.status_code == 404:
                return None  # there is no match
            raise

        html = parsers.html(resp.content, base_url=resp.url)

        titles = self._parse_titles(html)
        origin = self._parse_origin(html)

        return Film(
            url_csfd=resp.url,
            url_imdb=self._parse_imdb_url(html),
            title_main=titles.main,
            title_orig=titles.orig,
            titles_search=titles.others,
            year=origin.year,
            directors=list(self._iterparse_directors(html)),
            length=origin.length,
            rating_csfd=self._parse_rating(html),
            url_poster=self._parse_poster_url(html),
        )

    def _parse_imdb_url(self, html):
        imdb_img = html.cssselect_first('.links img.imdb')
        if imdb_img is not None:
            imdb_a = next(imdb_img.iterancestors(tag='a'))
            return imdb_a.get('href')
        return None

    def _parse_titles(self, html):
        info = html.cssselect_first('.content .info')

        # main title
        h1_el = info.cssselect_first('h1')
        main = h1_el.text.strip()

        # other titles
        title_el = html.cssselect_first('title')
        title_text = title_el.text_content()

        orig = None
        others = []
        for title in info.cssselect('.names h3'):
            other = title.text.strip()
            if re.search(r'/ ' + re.escape(other) + ' [\(\|]', title_text):
                orig = other
            others.append(other)

        return FilmTitles(main, orig, others)

    def _parse_origin(self, html):
        info = html.cssselect_first('.content .info')
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

    def _iterparse_directors(self, html):
        info = html.cssselect_first('.content .info')
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

    def _parse_poster_url(self, html):
        img = html.cssselect_first('#poster img')
        if img is None:
            return None  # no image?!

        url = img.get('src')
        if url.startswith('//'):
            url = 'https:' + url

        parts = urlparse.urlparse(url)
        if 'assets' in parts.path:
            return None  # default image

        # strip params so we get the largest image
        parts = (parts.scheme, parts.netloc, parts.path, None, None, None)
        return urlparse.urlunparse(parts)
