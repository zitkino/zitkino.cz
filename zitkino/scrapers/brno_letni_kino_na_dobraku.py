# -*- coding: utf-8 -*-


import re
import times
import requests

from zitkino import formats
from zitkino.models import Showtime, ScrapedFilm

from . import cinemas, scrapers


cinema = cinemas.register(
    name=u'Letní kino Na Dobráku',
    url='http://kinonadobraku.cz',
    street=u'Dobrovského 29',
    town=u'Brno',
    coords=(49.2181389, 16.5888692)
)


@scrapers.register
class Scraper(object):

    url = ('https://www.google.com/calendar/ical/n6a7pqdcgeprq9v7pf'
           '84dk3djo%40group.calendar.google.com/public/basic.ics')
    price = 90
    tags_map = {
        u'čes. tit.': 'subtitles',
        u'od 15 let': 'age15',
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
        resp = requests.get(self.url)
        cal = formats.ical(resp.content)
        for event in cal.walk():
            if event.name == 'VEVENT':
                yield event

    def _parse_event(self, event):
        starts_at = times.to_universal(event.get('dtstart').dt)
        title_main = event.get('summary')
        titles = [title_main]

        title_orig = year = length = None
        tags = []

        match = self.desc_re.match(event.get('description'))
        if match:
            if match.group('title'):
                title_orig = match.group('title').strip()
                titles.append(title_orig)

            year = int(match.group('year'))
            length = int(match.group('min'))

            tags = [self.tags_map.get(t.strip()) for t
                    in match.group('tags').split(',')]

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_main=title_main,
                title_orig=title_orig,
                titles=titles,
                year=year,
                length=length,
            ),
            starts_at=starts_at,
            tags=tags,
            price=self.price,
        )
