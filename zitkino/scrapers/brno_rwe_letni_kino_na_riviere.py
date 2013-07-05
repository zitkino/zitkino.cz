# -*- coding: utf-8 -*-


import requests

from zitkino import formats, parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import cinemas, scrapers


cinemas.register(
    name=u'RWE letní kino na Riviéře',
    url='http://www.kinonariviere.cz/',
    street=u'Bauerova 322/7',
    town=u'Brno',
    coords=(49.18827, 16.56924)
)


@scrapers.register
class Scraper(object):

    slug = 'brno_rwe_letni_kino_na_riviere'
    url = 'http://www.kinonariviere.cz/program'
    tags_map = {
        u'premiéra': 'premiere',
        u'titulky': 'subtitles',
    }

    def __call__(self):
        cinema = Cinema.objects.with_slug(self.slug).get()
        for row in self._scrape_rows():
            showtime = self._parse_row(row, self.url)
            showtime.cinema = cinema
            yield showtime

    def _scrape_rows(self):
        resp = requests.get(self.url)
        html = formats.html(resp.text)
        return html.cssselect('.content table tr')

    def _parse_row(self, row, base_url):
        starts_at = parsers.date_time_year(
            row[1].text_content(),
            row[2].text_content()
        )

        title_main = row[3].text_content()
        title_orig = row[4].text_content()

        tags = [self.tags_map.get(t) for t
                in (row[5].text_content(), row[6].text_content())]

        price = parsers.price(row[7].text_content())
        url_booking = row[8].link(base_url)

        return Showtime(
            film_scraped=ScrapedFilm(
                title_main=title_main,
                titles=[title_main, title_orig],
            ),
            starts_at=starts_at,
            tags=tags,
            url_booking=url_booking,
            price=price,
        )
