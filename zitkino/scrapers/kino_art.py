# -*- coding: utf-8 -*-


from zitkino import http
from zitkino import parsers
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
    title_blacklist = [u'Kinové prázdniny', u'KINO NEHRAJE']

    tags = {u'malý sál': None}

    def __call__(self):
        return self._parse_table(self._scrape_table())

    def _scrape_table(self):
        resp = http.get(self.url)
        html = parsers.html(resp.content, base_url=resp.url)
        return html.cssselect('#main .film_table tr')

    def _parse_table(self, rows):
        for row in rows[1:]:  # skip header
            for subrow in row[2].split('br'):
                showtime = self._parse_row(row, subrow)
                if showtime:
                    yield showtime
            for subrow in row[3].split('br'):  # small hall
                showtime = self._parse_row(row, subrow, tags=[u'malý sál'])
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

    def _parse_tag(self, el):
        name = el.text_content().strip(':')
        if name not in self.tags:
            resp = http.get(el.link())
            html = parsers.html(resp.content, base_url=resp.url)
            self.tags[name] = html.cssselect_first('#main h1').text_content()
        return name, self.tags[name]

    def _parse_row(self, row, subrow, tags=None):
        elements = self._parse_subrow(subrow)

        title_el = elements.get('title')
        if title_el is None:
            return None
        title_main = title_el.text_content()
        if title_main in self.title_blacklist:
            return None

        url = title_el.link()

        starts_at = parsers.date_time_year(
            row.cssselect('.film_table_datum')[0].text_content(),
            subrow.cssselect('.cas')[0].text_content(),
        )

        booking_el = elements.get('booking')
        url_booking = booking_el.link() if booking_el is not None else None

        tags = {tag: self.tags[tag] for tag in (tags or [])}
        tag_el = elements.get('tag')
        if tag_el is not None:
            tags.update([self._parse_tag(tag_el)])

        return Showtime(
            cinema=cinema,
            film_scraped=ScrapedFilm(
                title_scraped=title_main,
                url=url,
            ),
            starts_at=starts_at,
            tags=tags,
            url=self.url,
            url_booking=url_booking,
        )
