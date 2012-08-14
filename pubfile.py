# -*- coding: utf-8 -*-


import re
import os
import requests
from dateutil import rrule
from datetime import datetime, date, time
from hashlib import sha1
import urllib
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, Markup

import json


class Film(object):

    def __init__(self, cinema, date, title):
        self.cinema = cinema
        self.date = date
        self.title = title.upper()

    @property
    def hash(self):
        return sha1(
            str(self.cinema.name.encode('utf-8')) +
            str(datetime.combine(self.date.date(), time(0, 0))) +
            self.title.encode('utf8')
        ).hexdigest()


class Driver(object):

    name = ''
    url = ''

    def __init__(self):
        self.films = []

    def download(self):
        if not self.url:
            classname = self.__class__.__name__
            raise ValueError('No URL for driver {0}.'.format(classname))

        response = requests.get(self.url)
        response.raise_for_status()
        return response.content

    def decode(self, response):
        raise NotImplementedError

    def parse(self, soup):
        return []

    def scrape(self):
        if not self.films:
            self.films = list(self.parse(self.decode(self.download())))
        return self.films

    def __unicode__(self):
        return self.name


class SoupDriver(Driver):
    """Base class for beautiful soup drivers."""

    def decode(self, html):
        return BeautifulSoup(re.sub(r'\s+', ' ', html))


class JsonDriver(Driver):
    """Base class for JSON drivers."""
    def decode(self, src):
        return json.loads(src)


class DobrakDriver(SoupDriver):

    name = u'Dobrák'
    url = 'http://kinonadobraku.cz'
    web = 'http://kinonadobraku.cz'

    def parse(self, soup):
        dates = soup.select('#Platno .Datum_cas')
        names = soup.select('#Platno .Nazev')

        for date, name in zip(dates, names):
            date = re.sub(r'[^\d\-]', '', date['id'])
            film_date = datetime.strptime(date, '%Y-%m-%d')
            film_title = name.get_text().strip().upper()

            yield Film(self, film_date, film_title)


class StarobrnoDriver(SoupDriver):

    name = u'Starobrno'
    url = 'http://www.kultura-brno.cz/cs/film/starobrno-letni-kino-na-dvore-mestskeho-divadla-brno'
    web = 'http://www.letnikinobrno.cz'

    def parse(self, soup):
        for row in soup.select('.content tr'):
            cells = row.select('td')

            if len(cells) == 3:
                # date
                date = cells[1].get_text()
                match = re.search(r'(\d+)\.(\d+)\.', date)
                if not match:
                    continue

                film_date = datetime(
                    int(2012),
                    int(match.group(2)),
                    int(match.group(1))
                )

                # title
                film_title = cells[2].get_text()
                if not film_title:
                    continue

                yield Film(self, film_date, film_title)


class ArtDriver(JsonDriver):
    """Art driver using JSON API"""

    name = u'Art'
    url_base = 'http://www.kinoartbrno.cz/export/?start=%(date)s'
    url = url_base % {'date' : date.today() }
    web = 'http://www.kinoartbrno.cz'

    def parse(self, movies):
        movie_date = None
        movie_title = ''
        m_date_format = '%Y-%m-%d %H:%M:%S'

        for movie in movies:
            movie_date = datetime.strptime(movie['datum'], m_date_format)
            movie_title = movie['nazevCesky'].upper()

            yield Film(self, movie_date, movie_title)


class LucernaDriver(SoupDriver):

    name = u'Lucerna'
    url = 'http://www.kinolucerna.info/index.php?option=com_content&view=article&id=37&Itemid=61'
    web = 'http://www.kinolucerna.info'

    re_range = re.compile(r'(\d+)\.(\d+)\.-(\d+)\.(\d+)\.')

    def __init__(self):
        self.today = datetime.now()
        super(LucernaDriver, self).__init__()

    def get_date_ranges(self, dates_text):
        today = self.today
        for match in self.re_range.finditer(dates_text):
            start_day = int(match.group(1))
            end_day = int(match.group(3))

            start_month = int(match.group(2))
            end_month = int(match.group(4))

            start_year = today.year if today.month <= start_month else (today.year + 1)
            end_year = today.year if today.month <= end_month else (today.year + 1)

            start = datetime(start_year, start_month, start_day)
            end = datetime(end_year, end_month, end_day)

            for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                yield day

    def get_standalone_dates(self, dates_text):
        today = self.today
        dates_text = self.re_range.sub('', dates_text)
        for match in re.finditer(r'(\d+)\.(\d+)\.', dates_text):
            month = int(match.group(2))
            year = today.year if today.month <= month else (today.year + 1)
            yield datetime(year, month, int(match.group(1)))

    def parse(self, soup):
        for row in soup.select('.contentpaneopen strong'):
            text = row.get_text().strip()
            match = re.search(r'\d+:\d+', text)
            if match:
                text = re.split(r'[\b\s]+(?=\d+\.)', text, maxsplit=1)

                film_title = text[0].strip().upper()
                dates_text = text[1]

                date_ranges = self.get_date_ranges(dates_text)
                standalone_dates = self.get_standalone_dates(dates_text)

                dates = list(date_ranges) + list(standalone_dates)
                for film_date in dates:
                    yield Film(self, film_date, film_title)


def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.quote_plus(s)
    return Markup(s)


class Kino(object):

    drivers = (
        ArtDriver,
        DobrakDriver,
        LucernaDriver,
        StarobrnoDriver,
    )

    template_filters = {
        'format_date': lambda dt: dt.strftime('%d. %m.'),
        'format_date_ics': lambda dt: dt.strftime('%Y%m%d'),
        'format_timestamp_ics': lambda dt: dt.strftime('%Y%m%dT%H%M%SZ'),
        'urlencode': urlencode_filter,
    }

    templates_dir = './templates'
    html_template_name = 'kino.html'
    ics_template_name = 'kino.ics'

    html_filename = 'kino.html'
    ics_filename = 'static/kino.ics'

    output_dir = './output'

    def __init__(self):
        self.today = datetime.combine(date.today(), time(0, 0))

    def setup_jinja_env(self):
        jinja_env = Environment(loader=FileSystemLoader(self.templates_dir))
        jinja_env.filters.update(self.template_filters)
        return jinja_env

    def scrape_films(self):
        films = []
        for driver in self.drivers:
            films += list(driver().scrape())
        sorted_films = sorted(films, key=lambda film: film.date)
        filtered_films = [f for f in sorted_films if f.date >= self.today]
        return filtered_films

    def render_template(self, filename, films):
        jinja_env = self.setup_jinja_env()
        template = jinja_env.get_template(filename)
        return template.render(
            films=films,
            today=self.today,
            now=datetime.now()
        ).encode('utf8')

    def write_file(self, filename, contents):
        path = os.path.join(self.output_dir, filename)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(path, 'w') as f:
            f.write(contents)

    def run(self):
        films = self.scrape_films()

        html = self.render_template(self.html_template_name, films)
        ics = self.render_template(self.ics_template_name, films)

        self.write_file(self.html_filename, html)
        self.write_file(self.ics_filename, ics)

if __name__ == '__main__':
    Kino().run()
