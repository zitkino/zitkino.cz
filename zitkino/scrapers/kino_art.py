# -*- coding: utf-8 -*-


from zitkino import parsers
from zitkino.utils import download
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers


cinema = Cinema(
    name=u'Kino Art',
    url='http://www.kinoart.cz',
    street=u'Cihlářská 19',
    town=u'Brno',
    coords=(49.2043861, 16.6034708)
)


@scrapers.register(cinema)
class Scraper(object):

    url = 'http://www.kultura-brno.cz/cs/film/program-kina-art'
    title_blacklist = [u'Kinové prázdniny']
    default_price = 110
    price_map = {
        'seniors': 50,
        'children': 60,
    }
    tags_map = {
        u'SEN:': 'seniors',
    }

    def __call__(self):
        return self._parse_table(self._scrape_table())

    def _scrape_table(self):
        resp = download(self.url)
        html = parsers.html(resp.content, base_url=resp.url)
        return html.cssselect('#main .film_table tr')

    def _parse_table(self, rows):
        for row in rows[1:]:  # skip header
            for subrow in row[2].split('br'):
                showtime = self._parse_row(row, subrow)
                if showtime:
                    yield showtime

    def _parse_row(self, row, subrow):
        links = subrow.cssselect('a')
        if len(links) == 3:
            tag_el, title_el, booking_el = links
        else:
            tag_el = None
            title_el, booking_el = links

        title_main = title_el.text_content()
        if title_main in self.title_blacklist:
            return None

        starts_at = parsers.date_time_year(
            row.cssselect('.film_table_datum')[0].text_content(),
            subrow.cssselect('.cas')[0].text_content(),
        )
        tags = []
        price = self.default_price
        url_booking = booking_el.link()

        if tag_el is not None:
            tag = self.tags_map.get(tag_el.text_content())
            price = self.price_map.get(tag, self.default_price)
            tags.append(tag)

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main=title_main,
                titles=[title_main],
            ),
            starts_at=starts_at,
            tags=tags,
            url_booking=url_booking,
            price=price,
            prices={

            }
        )
