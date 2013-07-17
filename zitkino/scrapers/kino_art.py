# -*- coding: utf-8 -*-


from collections import namedtuple

from zitkino.utils import download
from zitkino import formats, parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers


cinema = Cinema(
    name=u'Kino Art',
    url='http://www.kinoart.cz',
    street=u'Cihlářská 19',
    town=u'Brno',
    coords=(49.2043861, 16.6034708)
)


Row = namedtuple('Row', ['date', 'time', 'tag', 'link', 'link_booking'])


@scrapers.register(cinema)
class Scraper(object):

    url = 'http://www.kultura-brno.cz/cs/film/program-kina-art'
    tags_map = {
        u'SEN': 'seniors',
    }
    blacklist = [u'Kinové prázdniny']
    default_price = 110
    price_map = {
        'seniors': 50,
        'children': 60,
    }

    def __call__(self):
        for row in self._scrape_rows():
            showtime = self._parse_row(row)
            if showtime:
                yield showtime

    def _scrape_rows(self):
        resp = download(self.url)
        html = formats.html(resp.content, base_url=resp.url)
        rows = html.cssselect('#main .film_table tr')

        for row in rows[1:]:  # skip table header
            for subrow in row[2].split('br'):
                yield self._merge(row, subrow)

    def _merge(self, row, subrow):
        date = row[1]
        tag = None
        if len(subrow) == 3:
            time, link, link_booking = subrow
        elif len(subrow) == 4:
            time, tag, link, link_booking = subrow
        else:
            raise ValueError('Unable to merge rows.')
        return Row(date, time, tag, link, link_booking)

    def _parse_row(self, row):
        title_main = row.link.text_content()
        if title_main in self.blacklist:
            return None

        starts_at = parsers.date_time_year(
            row.date.text_content(),
            row.time.text_content(),
        )

        tag = None
        price = self.default_price
        if row.tag is not None:
            tag = self.tags_map.get(row.tag.text_content())
            price = self.price_map.get(tag)

        url_booking = row.link_booking.link()

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main=title_main,
                titles=[title_main],
            ),
            starts_at=starts_at,
            tags=[tag],
            url_booking=url_booking,
            price=price,
        )
