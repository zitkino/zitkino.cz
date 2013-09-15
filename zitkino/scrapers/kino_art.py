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
    price_map = (
        ('seniors', 50),
        ('children', 80),
        ('small_hall', 100),
    )
    tags_map = {
        u'SEN:': 'seniors',
        u'ART DĚTEM:': 'children',
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
            for subrow in row[3].split('br'):  # small hall
                showtime = self._parse_row(row, subrow, tags=['small_hall'])
                if showtime:
                    yield showtime

    def _parse_subrow(self, subrow):
        links = subrow.cssselect('a')
        elements = {'tag': None, 'title': None, 'booking': None}

        for i, link in enumerate(links):
            if link.text_content() == 'R':
                elements['booking'] = link
                links.pop(i)

        count = len(links)
        if count == 2:
            elements['tag'] = links[0]
            elements['title'] = links[1]
        if count == 1:
            elements['title'] = links[0]

        return elements

    def _select_price(self, tags):
        for tag, price in self.price_map:
            if tag in tags:
                return price
        return self.default_price

    def _parse_row(self, row, subrow, tags=None):
        elements = self._parse_subrow(subrow)

        title_el = elements.get('title')
        if title_el is None:
            return None
        title_main = title_el.text_content()
        if title_main in self.title_blacklist:
            return None

        starts_at = parsers.date_time_year(
            row.cssselect('.film_table_datum')[0].text_content(),
            subrow.cssselect('.cas')[0].text_content(),
        )

        booking_el = elements.get('booking')
        url_booking = booking_el.link() if booking_el is not None else None

        tags = tags or []
        tag_el = elements.get('tag')
        if tag_el is not None:
            tags.append(self.tags_map.get(tag_el.text_content()))

        price = self._select_price(tags)

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
        )
