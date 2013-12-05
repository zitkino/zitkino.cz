# -*- coding: utf-8 -*-


import re
from datetime import date, time, datetime

import times

from zitkino import parsers
from zitkino.utils import download
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers


cinema = Cinema(
    name=u'Zimní kino',
    url='http://www.brnenskevanoce.cz/',
    street=u'Náměstí Svobody',
    town=u'Brno',
    coords=(49.19515, 16.608319)
)


@scrapers.register(cinema)
class Scraper(object):

    url = 'http://www.brnenskevanoce.cz/cs/program-brnenskych-vanoc'

    day_re = re.compile(r'^(\d{1,2})\.\s+.+$')
    title_re = re.compile(
        ur'(\d{2})\.(\d{2})\s+(([^–„](?!\d{2}\.\d{2}))+)\s+–\s+„Zimní kino“?'
    )

    def __call__(self):
        return self._parse_html(self._scrape_html())

    def _scrape_html(self):
        resp = download(self.url)
        return parsers.html(resp.content, base_url=resp.url)

    def _parse_html(self, html):
        y = times.now().year
        m = 11
        d = None

        for p in html.cssselect('.content p'):
            text = p.text_content().strip()
            match = self.day_re.match(text)
            if match:
                if 'prosinec' in text:
                    m += 1
                d = date(day=int(match.group(1)), month=m, year=y)
            elif u'Zimní kino' in text:
                match = self.title_re.search(text)
                if match:
                    t = time(
                        hour=int(match.group(1)),
                        minute=int(match.group(2))
                    )

                    starts_at = times.to_universal(
                        datetime.combine(d, t),
                        'Europe/Prague'
                    )
                    title_main = match.group(3)

                    yield Showtime(
                        cinema=cinema,
                        film_scraped=ScrapedFilm(
                            title_scraped=title_main,
                            titles=[title_main],
                        ),
                        starts_at=starts_at,
                    )
