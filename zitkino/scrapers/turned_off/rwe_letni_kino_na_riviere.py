# -*- coding: utf-8 -*-


from zitkino import http
from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers


cinema = Cinema(
    name=u'RWE letní kino na Riviéře',
    url='http://www.kinonariviere.cz/',
    street=u'Bauerova 322/7',
    town=u'Brno',
    coords=(49.18827, 16.56924)
)


@scrapers.register(cinema)
class Scraper(object):

    url = 'http://www.kinonariviere.cz/program'
    tags_map = {
        u'premiéra': u'premiéra',
        u'titulky': u'titulky',
    }

    def __call__(self):
        for row in self._scrape_rows():
            yield self._parse_row(row)

    def _scrape_rows(self):
        resp = http.get(self.url)
        html = parsers.html(resp.content, base_url=resp.url)
        return html.cssselect('.content table tr')

    def _parse_row(self, row):
        starts_at = parsers.date_time_year(
            row[1].text_content(),
            row[2].text_content()
        )

        title_main = row[3].text_content()
        title_orig = row[4].text_content()

        # TODO scrape tags according to new implementation of tags
        # presented in https://github.com/honzajavorek/zitkino.cz/issues/97
        tags = [self.tags_map.get(t) for t
                in (row[5].text_content(), row[6].text_content())]

        url_booking = row[8].link()

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main_scraped=title_main,
                title_orig_scraped=title_orig,
            ),
            starts_at=starts_at,
            tags={tag: None for tag in tags},
            url=self.url,
            url_booking=url_booking,
        )
