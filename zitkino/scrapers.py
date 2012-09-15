# -*- coding: utf-8 -*-


import re
import json
import requests
import times
from dateutil import rrule
from bs4 import BeautifulSoup
from datetime import datetime, date


class ScrapedShowtime(object):

    def __init__(self, cinema_slug, starts_at, film_title):
        self.cinema_slug = cinema_slug
        self.starts_at = starts_at
        self.film_title = film_title


### Abstract scrapers ###


class Scraper(object):
    """Base scraper class."""

    url = ''
    timezone = 'UTC'

    def __init__(self, now):
        self.films = []
        self._now = now

    @property
    def now(self):
        """Convert current datetime to scraper's timezone."""
        return times.to_local(self._now, self.timezone)

    def to_utc(self, dt):
        """Convert given datetime from scraper's timezone to UTC."""
        return times.to_universal(dt, self.timezone)

    def download(self):
        """Download data document (HTML, JSON, whatever)."""
        if not self.url:
            classname = self.__class__.__name__
            raise ValueError('No URL for driver {0}.'.format(classname))

        response = requests.get(self.url)
        response.raise_for_status()
        return response.content

    def decode(self, content):
        """Decode document's contents, return data structure."""
        raise NotImplementedError

    def parse(self, decoded_content):
        """Parse decoded content and return showtimes."""
        return []

    def scrape(self):
        """Download data, parse it, return showtimes."""
        if not self.films:
            content = self.decode(self.download())
            self.films = list(self.parse(content))
        return self.films


class SoupScraper(Scraper):
    """Base scraper class for processing HTML documents."""
    def decode(self, content):
        """Turn content into HTML soup."""
        return BeautifulSoup(re.sub(r'\s+', ' ', content))


class JsonScraper(Scraper):
    """Base scraper class for processing JSON documents."""
    def decode(self, content):
        """Turn JSON content into Python dict."""
        return json.loads(content)


### Cinema-specific scrapers ###


class LetniKinoNaDobrakuScraper(SoupScraper):
    """Scraper for Letní kino Na Dobráku."""

    url = 'http://kinonadobraku.cz'
    cinema_slug = 'brno-letni-kino-na-dobraku'
    timezone = 'Europe/Prague'

    def parse(self, decoded_content):
        soup = decoded_content

        dates = soup.select('#Platno .Datum_cas')
        names = soup.select('#Platno .Nazev')

        film_date_format = '%Y-%m-%d'

        for date, name in zip(dates, names):
            date = re.sub(r'[^\d\-]', '', date['id'])
            film_date = datetime.strptime(date, film_date_format)
            film_title = name.get_text(separator='\n', strip=True).upper()

            yield ScrapedShowtime(self.cinema_slug,
                                  self.to_utc(film_date),
                                  film_title)


class StarobrnoLetniKinoScraper(SoupScraper):
    """Scraper for Starobrno letní kino."""

    url = 'http://www.kultura-brno.cz/cs/film/starobrno-letni-kino-na-dvore-'\
        'mestskeho-divadla-brno'
    cinema_slug = 'brno-starobrno-letni-kino'
    timezone = 'Europe/Prague'

    def parse(self, decoded_content):
        soup = decoded_content

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

                yield ScrapedShowtime(
                    self.cinema_slug,
                    self.to_utc(film_date),
                    film_title)


class KinoLucernaScraper(SoupScraper):
    """Scraper for Kino Lucerna."""

    url = 'http://www.kinolucerna.info/index.php?option=com_content'\
        '&view=article&id=37&Itemid=61'
    cinema_slug = 'brno-kino-lucerna'
    timezone = 'Europe/Prague'

    _range_re = re.compile(r'(\d+)\.(\d+)\.-(\d+)\.(\d+)\.')

    def get_date_ranges(self, dates_text):
        today = self.now
        next_year = today.year + 1

        for match in self._range_re.finditer(dates_text):
            start_day = int(match.group(1))
            end_day = int(match.group(3))

            start_month = int(match.group(2))
            end_month = int(match.group(4))

            start_year = today.year if today.month <= start_month\
                else next_year
            end_year = today.year if today.month <= end_month\
                else next_year

            start = datetime(start_year, start_month, start_day)
            end = datetime(end_year, end_month, end_day)

            for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                yield day

    def get_standalone_dates(self, dates_text):
        today = self.today
        dates_text = self._range_re.sub('', dates_text)
        for match in re.finditer(r'(\d+)\.(\d+)\.', dates_text):
            month = int(match.group(2))
            year = today.year if today.month <= month else (today.year + 1)
            yield datetime(year, month, int(match.group(1)))

    def parse(self, decoded_content):
        soup = decoded_content

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
                    yield ScrapedShowtime(
                        self.cinema_slug,
                        self.to_utc(film_date),
                        film_title)


class KinoArtScraper(JsonScraper):
    """Scraper for Kino Art."""

    _url_base = 'http://www.kinoartbrno.cz/export/?start={date}'

    url = _url_base.format(date=date.today())
    cinema_slug = 'brno-kino-art'
    timezone = 'Europe/Prague'

    def parse(self, decoded_content):
        films = decoded_content

        film_title = ''
        film_date_format = '%Y-%m-%d %H:%M:%S'

        for film in films:
            film_date = datetime.strptime(film['datum'], film_date_format)
            film_title = film['nazevCesky']

            yield ScrapedShowtime(self.cinema_slug,
                                  self.to_utc(film_date),
                                  film_title)
