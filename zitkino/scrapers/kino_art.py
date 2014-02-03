# -*- coding: utf-8 -*-


import re
import datetime

import times

from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers, Scraper


cinema = Cinema(
    name=u'Kino Art',
    url='http://www.kinoart.cz',
    street=u'Cihlářská 19',
    town=u'Brno',
    coords=(49.2043861, 16.6034708)
)


@scrapers.register(cinema)
class KinoartScraper(Scraper):

    url = 'http://kinoart.cz/program/'
    title_blacklist = [u'Kinové prázdniny', u'KINO NEHRAJE']

    def __call__(self):
        resp = self.session.get(self.url)
        html = parsers.html(resp.content, base_url=resp.url)

        for table in html.cssselect('.program'):
            tag = table.cssselect_first('.title').text_content().lower()
            for row in table.cssselect('tr'):
                yield self._parse_row(row, tags={tag: None})

    def _parse_row(self, row, tags=None):
        movie_el = row.cssselect_first('.movie a:not(.tag)')
        url = movie_el.link()
        title = movie_el.text_content()

        date_el = row.cssselect_first('.date').text_content(whitespace=True)
        date, time = re.split(r'[\r\n]+', date_el)

        starts_at = times.to_universal(datetime.datetime.combine(
            parsers.date_cs(date),
            datetime.time(*[int(n) for n in time.split(':')])
        ), 'Europe/Prague')

        tags = self._parse_tags(row, tags)
        details = self._parse_details(url)

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main_scraped=title,
                url=url,
                **details
            ),
            starts_at=starts_at,
            tags=tags,
            url=self.url,
        )

    def _parse_tags(self, row, tags=None):
        tags = tags or {}
        for a in row.cssselect('.movie a.tag'):
            resp = self.session.get(a.link())
            html = parsers.html(resp.content, base_url=resp.url)
            tags[a.text_content()] = html.cssselect_first('h1').text_content()
        return tags

    def _parse_details(self, url):
        data = {}

        resp = self.session.get(url)
        html = parsers.html(resp.content, base_url=resp.url)
        content = html.cssselect_first('#content .leftcol')

        image = content.cssselect_first('img.wp-post-image')
        if image is not None:
            data['url_poster'] = self._parse_image_link(image)

        csfd_link = content.cssselect_first('a.csfd')
        if csfd_link is not None and csfd_link.get('href') != 'http://':
            data['url_csfd'] = csfd_link.get('href')

        imdb_link = content.cssselect_first('a.imdb')
        if imdb_link is not None and imdb_link.get('href') != 'http://':
            data['url_imdb'] = imdb_link.get('href')

        if 'trailer' in content.text_content().lower():
            for iframe in content.cssselect('iframe'):
                try:
                    url = parsers.youtube_url(iframe.get('src'))
                    data['url_trailer'] = url
                except ValueError:
                    pass

        return data

    def _parse_image_link(self, image):
        return re.sub(r'\-\d+x\d+(\.\w+)$', r'\1', image.get('src'))
