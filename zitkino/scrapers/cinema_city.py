# -*- coding: utf-8 -*-


import re
import datetime

import times

from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from . import scrapers, Scraper


class CinemacityScraper(Scraper):

    url = ('http://www.cinemacity.cz/scheduleInfo?locationId={location_id}'
           '&date={date:%d/%m/%Y}')

    location_id = None
    cinema = None

    tag_re = (
        (re.compile(r' 3[dD]$'), '3D'),
    )

    def __call__(self):
        day = datetime.date.today()
        while True:
            resp = self.session.get(self.url.format(
                location_id=self.location_id,
                date=day
            ))
            html = parsers.html(resp.content, base_url=resp.url)

            if u'Žádný program' in html.text_content():
                break

            table = html.cssselect('tr')
            labels = table[0]
            rows = table[1:]

            for row in rows:
                for st in self._parse_row(day, row, labels):
                    yield st

            day += datetime.timedelta(days=1)

    def _parse_row(self, day, row, labels):
        a = row.cssselect_first('a.featureLink')
        title = a.text_content()
        url = a.link()

        details = self._parse_details(url)
        tags = {}
        showtimes = []

        row = list(row.iterchildren())[1:]
        labels = list(labels.iterchildren())[1:]
        table = [
            (c.text_content(), l.text_content())
            for (c, l) in zip(row, labels)
        ]

        for cell, label in table:
            if label:
                if label == 'Min.':
                    details.setdefault('length', int(cell))
                elif cell != '---':
                    tags[cell] = label
            elif cell:
                showtimes.extend(cell.split())

        for regexp, tag in self.tag_re:
            if regexp.search(title):
                tags[tag] = None
                title = regexp.sub('', title).strip()

        for st in showtimes:
            starts_at = times.to_universal(datetime.datetime.combine(
                day,
                datetime.time(*[int(n) for n in st.split(':')])
            ), 'Europe/Prague')

            yield Showtime(
                cinema=self.cinema,
                film_scraped=ScrapedFilm(
                    title_main_scraped=title,
                    **details
                ),
                starts_at=starts_at,
                tags=tags,
                url='http://www.cinemacity.cz/',
            )

    def _parse_details(self, url):
        resp = self.session.get(url)
        html = parsers.html(resp.content, base_url=resp.url)

        info = {}
        for row in html.cssselect('.feature_info_row'):
            label = row.cssselect_first('.pre_label')
            info[label.text_content()] = label.getnext().text_content()

        return {
            'title_orig': info.get(u'Name:'),
            'length': info.get(u'Délka (min.):'),
            # not taking the year, because they use year of Czech premiere,
            # instead of the year of the original release
        }


cinema_olympia = Cinema(
    name=u'Cinema City Olympia',
    url='http://www.cinemacity.cz/olympia',
    street=u'U Dálnice 777',
    town=u'Modřice',
    coords=(49.1381280, 16.6330180),
    is_multiplex=True,
)


@scrapers.register(cinema_olympia)
class OlympiaScraper(CinemacityScraper):

    location_id = '1010103'
    cinema = cinema_olympia


cinema_velkyspalicek = Cinema(
    name=u'Cinema City Velký Špalíček',
    url='http://www.cinemacity.cz/velkyspalicek',
    street=u'Mečová 2',
    town=u'Brno',
    coords=(49.1932758, 16.6069739),
    is_multiplex=True,
)


@scrapers.register(cinema_velkyspalicek)
class VelkyspalicekScraper(CinemacityScraper):

    location_id = '1010107'
    cinema = cinema_velkyspalicek
