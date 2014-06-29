# -*- coding: utf-8 -*-


import re
import datetime

import times
from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers, Scraper


cinema = Cinema(
    name=u'Letní kino na dvoře MDB',
    url='http://www.letnikinobrno.cz/',
    street=u'Lidická 1863/16',
    town=u'Brno',
    coords=(49.2015431, 16.6082542)
)


@scrapers.register(cinema)
class LetniKinoMDBScraper(Scraper):

    url = 'http://www.letnikinobrno.cz/program-kina/'

    def __call__(self):
        for item in self._scrape_rows():
            yield self._parse_item(item)

    def _scrape_rows(self):
        resp = self.session.get(self.url)
        html = parsers.html(resp.content, base_url=resp.url)
        return html.cssselect('.program-item')

    def _parse_item(self, item):
        title_main = item.cssselect_first('.program-title').text_content()
        url = item.cssselect_first('.program-title').link()

        date_el = item.cssselect_first('.program-date').text_content()
        date, time = re.split(r'\s+ve?\s+', date_el)

        starts_at = times.to_universal(datetime.datetime.combine(
            parsers.date_cs(date),
            datetime.time(*[int(n) for n in time.split(':')])
        ), 'Europe/Prague')

        details = self._parse_details(url)

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main_scraped=title_main,
                url=url,
                **details
            ),
            starts_at=starts_at,
            url=self.url,
        )

    def _parse_details(self, url):
        data = {}

        resp = self.session.get(url)
        html = parsers.html(resp.content, base_url=resp.url)
        content = html.cssselect_first('#content #right')

        image = content.cssselect_first('a.rel')
        if image is not None:
            data['url_posters'] = [image.link()]

        csfd_link = content.cssselect_first('a[href^="http://www.csfd.cz"]')
        if csfd_link is not None:
            data['url_csfd'] = csfd_link.get('href')

        return data
