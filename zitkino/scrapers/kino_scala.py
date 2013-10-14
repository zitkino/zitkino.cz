# -*- coding: utf-8 -*-


import datetime

import times

from zitkino import parsers
from zitkino.utils import download
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers


cinema = Cinema(
    name=u'Kino Scala',
    url='http://www.kinoscala.cz',
    street=u'Moravské náměstí 3/127',
    town=u'Brno',
    coords=(49.1974, 16.6082)
)


@scrapers.register(cinema)
class Scraper(object):

    url = 'http://www.kinoscala.cz/cz/program/'

    tz = 'Europe/Prague'

    def __call__(self):
        date = None
        for row in self._scrape_rows():
            if row.has_class('day'):
                date = parsers.date_cs(row.text_content())
            else:
                yield self._parse_row(row, date)

    def _scrape_rows(self):
        """Generates individual table rows of cinema's calendar."""
        url = self.url

        while True:
            resp = download(url)
            html = parsers.html(resp.content, base_url=url)
            for el in html.cssselect('#content table tr'):
                yield el

            pagination = html.cssselect('#classic-paging a.forward')
            if pagination:
                url = pagination[0].link()
            else:
                break

    def _parse_time(self, el, date):
        """Parses time from given element, combines it with given date and
        returns corresponding datetime object in UTC.
        """
        time = datetime.time(*[int(t) for t in el.text_content().split(':')])
        dt = datetime.datetime.combine(date, time)
        return times.to_universal(dt, timezone=self.tz)

    def _parse_film(self, el):
        """Takes element with film's name and link to details.
        Returns film object.
        """
        title_main = el.xpath('.//a')[0].text_content()
        return ScrapedFilm(
            title_main=title_main,
            titles=[title_main],
        )

    def _parse_tags_from_icons(self, el):
        """Takes element with icons, turns them into tags."""
        return (el.text_content() for el in el.xpath('.//acronym'))

    def _parse_tags_from_cycles(self, el):
        """Takes element with labels about film cycles,
        turns them into tags.
        """
        return (
            el.text_content() for el in el.xpath('.//acronym')
            if el.has_class('cycle_name') and el.has_class('shortcut')
        )

    def _parse_row(self, row, date):
        """Takes single row and date information, returns
        :class:`~zitkino.models.Showtime` object.
        """
        st = Showtime(cinema=cinema, tags=[])

        for cell in row:
            if cell.has_class('col_time_reservation'):
                st.starts_at = self._parse_time(cell, date)
                st.url_booking = cell.link()

            if cell.has_class('col_movie_name'):
                st.film_scraped = self._parse_film(cell)

            if cell.has_class('col_param_icons'):
                st.tags.extend(self._parse_tags_from_icons(cell))

            if cell.has_class('col_cycle'):
                st.tags.extend(self._parse_tags_from_cycles(cell))

        return st
