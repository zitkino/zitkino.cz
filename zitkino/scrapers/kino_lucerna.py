# -*- coding: utf-8 -*-


import re
from datetime import datetime, time

import times

from zitkino import parsers
from zitkino.models import Cinema, Showtime, ScrapedFilm

from zitkino.scrapers import scrapers, Scraper


cinema = Cinema(
    name=u'Kino Lucerna',
    url='http://www.kinolucerna.info',
    street=u'Minská 19',
    town=u'Brno',
    coords=(49.2104939, 16.5855358)
)


@scrapers.register(cinema)
class KinolucernaScraper(Scraper):

    url = 'http://kinolucerna.info/index.php/program'
    url_booking = 'http://kinolucerna.info/index.php/rezervace'

    tz = 'Europe/Prague'

    tag_re = (
        # order is not arbitrary!
        (re.compile(ur'[–\-] titulky', re.I), u'titulky'),
        (re.compile(ur'[–\-] (český )?dabing', re.I), u'dabing'),
        (re.compile(ur' titulky', re.I), u'titulky'),
        (re.compile(ur' (český )?dabing', re.I), u'dabing'),
        (re.compile(r've? 2[dD]$'), '2D'),
        (re.compile(r've? 3[dD]$'), '3D'),
        (re.compile(r' 2[dD]$'), '2D'),
        (re.compile(r' 3[dD]$'), '3D'),
    )

    def __call__(self):
        resp = self.session.get(self.url)
        html = parsers.html(resp.content, base_url=resp.url)

        for event in html.cssselect('.event'):
            header = event.cssselect_first('h2')

            url = header.link()
            title = header.text_content()

            title_parts = title.split('/')
            if len(title_parts) == 2:
                # naive, but for now good enough
                title_main, title_orig = title_parts
            else:
                title_main = title
                title_orig = None

            details = event.cssselect_first('.descshort').text_content()
            cat = event.cssselect_first('.title-cat').text_content().lower()

            tags = []
            for regexp, tag in self.tag_re:
                if regexp.search(title_main):
                    tags.append(tag)
                    title_main = regexp.sub('', title_main).strip()
                if title_orig and regexp.search(title_orig):
                    tags.append(tag)
                    title_orig = regexp.sub('', title_orig).strip()
                if regexp.search(details):
                    tags.append(tag)
            if cat != 'filmy':
                tags.append(cat)

            d = parsers.date_cs(
                event.cssselect_first('.nextdate strong').text
            )

            t = event.cssselect_first('.nextdate .evttime').text_content()
            t = time(*map(int, t.split(':')))

            starts_at = times.to_universal(datetime.combine(d, t), self.tz)

            yield Showtime(
                cinema=cinema,
                film_scraped=ScrapedFilm(
                    title_main_scraped=title_main,
                    title_orig=title_orig or None,
                ),
                starts_at=starts_at,
                url=url,
                url_booking=self.url_booking,
                tags={tag: None for tag in tags},
            )
