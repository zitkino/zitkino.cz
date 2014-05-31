# -*- coding: utf-8 -*-


import re
import datetime
from collections import namedtuple

import times

from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers, Scraper


cinema = Cinema(
    name=u'Kino Scala',
    url='http://www.kinoscala.cz',
    street=u'Moravské náměstí 3/127',
    town=u'Brno',
    coords=(49.1974, 16.6082)
)


Row = namedtuple('Row', ['element', 'url'])


FilmInfo = namedtuple('FilmInfo', ['title', 'tags', 'url'])


@scrapers.register(cinema)
class KinoscalaScraper(Scraper):

    url = 'http://www.kinoscala.cz/cz/program/'

    tag_re = (
        # order is not arbitrary!
        (re.compile(ur'[–\-] titulky', re.I), u'titulky'),
        (re.compile(ur'[–\-] (český )?dabing', re.I), u'dabing'),
        (re.compile(ur' titulky', re.I), u'titulky'),
        (re.compile(ur' (český )?dabing', re.I), u'dabing'),
        (re.compile(r've? 2[dD]$'), '2D'),
        (re.compile(r've? 3[dD]$'), '3D'),
        (re.compile(r' 2[dD]$'), '2D'),
        (re.compile(r' 3[dD]$'), '3D'),
    )

    def __call__(self):
        date = None
        for row in self._scrape_rows():
            if row.element.has_class('day'):
                date = parsers.date_cs(row.element.text_content())
            else:
                yield self._parse_row(row.element, date, row.url)

    def _scrape_rows(self):
        """Generates individual table rows of cinema's calendar."""
        url = self.url

        while True:
            resp = self.session.get(url)
            html = parsers.html(resp.content, base_url=url)
            for el in html.cssselect('#content table tr'):
                yield Row(el, url)

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
        return times.to_universal(dt, timezone='Europe/Prague')

    def _parse_info(self, el):
        """Takes element with film's name and link to a page with details,
        returns object with film's details.
        """
        title_el = el.xpath('.//a')[0]
        title_main = title_el.text_content()
        url = title_el.link()

        tags = []
        for regexp, tag in self.tag_re:
            if regexp.search(title_main):
                tags.append(tag)
                title_main = regexp.sub('', title_main).strip()

        return FilmInfo(title_main, tags, url)

    def _parse_tags_from_icons(self, el):
        """Takes element with icons, turns them into tags."""
        for acronym in el.xpath('.//acronym'):
            yield (
                acronym.text_content(),
                acronym.get('title', acronym.get('data-original-title', None))
            )

    def _parse_tags_from_cycles(self, el):
        """Takes element with labels about film cycles,
        turns them into tags.
        """
        for icon in el.cssselect('.cycle_icon'):
            yield (
                icon.cssselect_first('.cycle_name.shortcut').text_content(),
                icon.cssselect_first('.cycle_name.full_name').text_content()
            )

    def _parse_row(self, row, date, url):
        """Takes single row and date information, returns
        :class:`~zitkino.models.Showtime` object.
        """
        st = Showtime(cinema=cinema, url=url)
        tags = {}

        for cell in row:
            if cell.has_class('col_time_reservation'):
                st.starts_at = self._parse_time(cell, date)
                st.url_booking = cell.link()

            if cell.has_class('col_movie_name'):
                info = self._parse_info(cell)
                st.film_scraped = ScrapedFilm(
                    title_main_scraped=info.title,
                    url=info.url,
                    **self._parse_details(info.url)
                )
                tags.update({tag: None for tag in info.tags})

            if cell.has_class('col_param_icons'):
                tags.update(self._parse_tags_from_icons(cell))

            if cell.has_class('col_cycle'):
                tags.update(self._parse_tags_from_cycles(cell))

        st.tags = tags
        return st

    def _parse_details(self, url):
        data = {}

        resp = self.session.get(url)
        html = parsers.html(resp.content, base_url=url)
        html.make_links_absolute()
        content = html.cssselect_first('.content_main')

        image = content.cssselect_first('.movie_image img')
        if image is not None:
            data['url_posters'] = [image.get('src')]

        for a in content.cssselect('a'):
            try:
                url = parsers.youtube_url(a.get('href'))
                data['url_trailer'] = url
                break
            except ValueError:
                pass

            if 'csfd.cz' in a.get('href'):
                data['url_csfd'] = a.get('href')

            if 'imdb.com' in a.get('href'):
                data['url_imdb'] = a.get('href')

        return data
