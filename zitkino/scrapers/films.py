# -*- coding: utf-8 -*-

from fuzzywuzzy import fuzz

from zitkino.scrapers.common import Scraper, SoupDecoder


class FilmRecognizer(SoupDecoder, Scraper):

    url = 'http://www.csfd.cz/hledat/'
    accept_ratio = 80

    def _parse(self, decoded_content):
        """Parse decoded content and return results."""
        soup = decoded_content

        # ČSFD sometimes redirects directly to film's profile page
        found = soup.select('#search-films h3') or soup.select('#profile h1')

        try:
            title = found[0]
            return title.get_text().strip()
        except IndexError:
            return None

    def _is_similar(self, title1, title2):
        ratio = fuzz.partial_ratio(
            title1.lower(), title2.lower())
        print ratio
        return ratio >= self.accept_ratio

    def scrape(self, title):
        """Return normalized film title."""
        content = self._decode(self._download(q=title))
        parsed_title = self._parse(content)

        print parsed_title, title
        if parsed_title and self._is_similar(parsed_title, title):
            return parsed_title
        return None
