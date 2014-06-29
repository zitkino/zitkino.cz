# -*- coding: utf-8 -*-


import re

import times

from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers, Scraper


cinema = Cinema(
    name=u'Letní kino Na Dobráku',
    url='http://kinonadobraku.cz',
    street=u'Dobrovského 29',
    town=u'Brno',
    coords=(49.2181389, 16.5888692)
)


@scrapers.register(cinema)
class LetnikinonadobrakuScraper(Scraper):

    url = ('https://www.google.com/calendar/ical/n6a7pqdcgeprq9v7pf'
           '84dk3djo%40group.calendar.google.com/public/basic.ics')
    tags_map = {
        u'čes. tit.': u'české titulky',
        u'od 15 let': u'od 15 let',
    }
    desc_re = re.compile(r'''
        (?P<title>([^\n]+)\n)?  # first line with alternative title
        \D+                     # garbage
        (?P<year>\d{4})         # year
        \D+                     # garbage
        (?P<min>\d+)            # minutes
        \s*min\.?               # garbage
        (?P<tags>[^\n]*)        # tags
    ''', re.U | re.X)

    def __call__(self):
        for event in self._scrape_events():
            yield self._parse_event(event)

    def _scrape_events(self):
        resp = self.session.get(self.url)
        cal = parsers.ical(resp.content)
        for event in cal.walk():
            if event.name == 'VEVENT':
                yield event

    def _parse_event(self, event):
        starts_at = times.to_universal(event.get('dtstart').dt)
        title_main = event.get('summary')

        title_orig = year = length = None
        tags = []

        match = self.desc_re.match(event.get('description'))
        if match:
            if match.group('title'):
                title_orig = match.group('title').strip()

            year = int(match.group('year'))
            length = int(match.group('min'))

            # TODO scrape tags according to new implementation of tags
            # presented in https://github.com/honzajavorek/zitkino.cz/issues/97
            tags = [self.tags_map.get(t.strip()) for t
                    in match.group('tags').split(',')]

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main_scraped=title_main,
                title_orig_scraped=title_orig,
                year=year,
                length=length,
            ),
            starts_at=starts_at,
            tags={tag: None for tag in tags if tag},
            url='http://kinonadobraku.cz',
        )
