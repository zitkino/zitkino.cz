# -*- coding: utf-8 -*-


import re
import datetime

import times

from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers, Scraper


cinema = Cinema(
    name=u'Kinokavárna',
    url='http://www.kinokavarna.cz/',
    street=u'Náměstí SNP 33',
    town=u'Brno',
    coords=(49.2179300, 16.6207072)
)


@scrapers.register(cinema)
class KinokavarnaScraper(Scraper):

    url = 'http://www.kinokavarna.cz/program.html'

    length_re = re.compile(r'(\d+)\s*(min|min\.|minut)')
    year_re = re.compile(r'\d{4}')
    time_re = re.compile(r'(\d{1,2})[:\.](\d{2})')

    def __call__(self):
        resp = self.session.get(self.url)
        html = parsers.html(resp.content, base_url=resp.url)

        for entry in html.cssselect('#content-in .aktuality'):
            st = self._parse_entry(entry)
            if st:
                yield st

    def _parse_entry(self, entry):
        try:
            description = next(
                line for line
                in entry.text_content(whitespace=True).splitlines()
                if self.length_re.search(line)
            )
        except StopIteration:
            return None  # it's not a film

        date_el = entry.cssselect_first('h4 span')
        date = datetime.datetime(*reversed(
            [int(n) for n in date_el.text_content().split('.')]
        ))

        time_el = entry.cssselect_first('.start')
        time_match = self.time_re.search(time_el.text_content())
        time = datetime.time(
            int(time_match.group(1)),
            int(time_match.group(2)),
        )

        starts_at = times.to_universal(
            datetime.datetime.combine(date, time),
            'Europe/Prague'
        )
        title = date_el.tail

        tags = {}
        detail_data = {}

        details = [detail.strip() for detail in description.split(',')]
        for detail in details:
            if self.year_re.match(detail):
                detail_data['year'] = int(detail)

            match = self.length_re.match(detail)
            if match:
                detail_data['length'] = int(match.group(1))

            if 'tit.' in detail or 'titulky' in detail or 'dabing' in detail:
                tags[detail] = None

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main_scraped=title,
                **detail_data
            ),
            starts_at=starts_at,
            tags=tags,
            url=self.url,
        )
