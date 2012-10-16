# -*- coding: utf-8 -*-

import re
import logging

from zitkino.scrapers.common import Scraper, SoupDecoder
from zitkino.models import Film


### ČSFD film recognizer ###


class CSFDFilmRecognizer(SoupDecoder, Scraper):

    url = 'http://www.csfd.cz/hledat/'

    _id_csfd_re = re.compile(r'/film/(\d+)\D')
    _id_imdb_re = re.compile(r'/tt(\d+)/?')
    _year_re = re.compile(r'[,\s]+(\d{4})[,\s]+')
    _length_re = re.compile(r'(\d+)\s+min')

    def __init__(self, *args, **kwargs):
        self._log = logging.getLogger(__name__)
        super(CSFDFilmRecognizer, self).__init__(*args, **kwargs)

    def _extract_id_csfd(self, url):
        match = self._id_csfd_re.search(url)
        return int(match.group(1)) if match else None

    def _extract_id_imdb(self, url):
        match = self._id_imdb_re.search(url)
        return int(match.group(1)) if match else None

    def _extract_title_main(self, soup):
        title_html_main = soup.select('#profile h1')
        try:
            h1 = title_html_main[0]
            spans = h1.span
            if spans:
                spans.extract()
            return h1.get_text().strip()
        except IndexError:
            return None

    def _extract_titles_alt(self, soup):
        title_html_alt = soup.select('#profile .names li')
        return [t.get_text().strip() for t in title_html_alt]

    def _extract_url_imdb(self, soup):
        for link_html in soup.select('#share .links a'):
            if 'imdb.com' in link_html['href']:
                return link_html['href']
        return None

    def _extract_year(self, soup):
        try:
            origin = soup.select('#profile .origin')[0].get_text().strip()
        except IndexError:
            return None
        match = self._year_re.search(origin)
        return int(match.group(1)) if match else None

    def _extract_length(self, soup):
        try:
            origin = soup.select('#profile .origin')[0].get_text().strip()
        except IndexError:
            return None
        match = self._length_re.search(origin)
        return int(match.group(1)) if match else None

    def _extract_rating_csfd(self, soup):
        try:
            text = soup.select('#rating .average')[0].get_text().strip()
            return float(text.strip('%')) / 100
        except (IndexError, ValueError):
            return None

    def _parse(self, decoded_content, response=None):
        """Parse decoded content and return results."""
        soup = decoded_content
        url = response.url

        link = soup.select('#search-films h3 a')
        if link:
            # search results, get the first result
            url = 'http://www.csfd.cz' + link[0]['href']
            response = self._download(url)
            soup = self._decode(response.content)

        # else, ČSFD sometimes redirects directly to film's profile page

        film = Film()
        film.url_csfd = url
        film.id_csfd = self._extract_id_csfd(url)

        title_main = self._extract_title_main(soup)
        film.title_main = title_main
        film.titles = [title_main] + self._extract_titles_alt(soup)

        url_imdb = self._extract_url_imdb(soup)
        if url_imdb:
            film.url_imdb = url_imdb
            film.id_imdb = self._extract_id_imdb(url_imdb)

        film.year = self._extract_year(soup)
        film.length = self._extract_length(soup)
        film.rating_csfd = self._extract_rating_csfd(soup)

        return film

    def scrape(self, scraped_showtime):
        """Return a film object."""
        title = scraped_showtime.film_title

        response = self._download(self.url, q=title)
        content = self._decode(response.content)
        film = self._parse(content, response)

        if film.has_similar_title(title):
            return film
        return None
