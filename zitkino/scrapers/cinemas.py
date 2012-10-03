# -*- coding: utf-8 -*-


import re
import times
import logging
from dateutil import rrule
from datetime import datetime, date

from zitkino.scrapers.common import Scraper as BaseScraper, \
    SoupDecoder, JsonDecoder
from zitkino.utils import repr_name


### Utils ###


active_scrapers = []


def active_scraper(cls):
    """Decorate class to register it as an active scraper."""
    active_scrapers.append(cls)
    return cls


### Data structure for results ###


class ScrapedShowtime(object):

    def __init__(self, cinema_slug, starts_at, film_title):
        self.cinema_slug = cinema_slug
        self.starts_at = starts_at
        self.film_title = film_title

    def __repr__(self):
        return '<{name} {film_title!r}@{cinema_slug}, {starts_at}>'.format(
            name=repr_name(self.__class__), **vars(self))


### Abstract scraper ###


class Scraper(BaseScraper):
    """Base scraper class."""

    url = ''
    timezone = 'UTC'

    def __init__(self, now, user_agent=None):
        self._now = now
        self._log = logging.getLogger(__name__)
        super(Scraper, self).__init__(user_agent=user_agent)

    @property
    def now(self):
        """Convert current datetime to scraper's timezone."""
        return times.to_local(self._now, self.timezone)

    def _to_utc(self, dt):
        """Convert given datetime from scraper's timezone to UTC."""
        return times.to_universal(dt, self.timezone)


### Cinema-specific scrapers ###


@active_scraper
class LetniKinoNaDobrakuScraper(SoupDecoder, Scraper):
    """Scraper for Letní kino Na Dobráku."""

    url = 'http://kinonadobraku.cz'
    cinema_slug = 'brno-letni-kino-na-dobraku'
    timezone = 'Europe/Prague'

    _date_id_re = re.compile(r'[^\d\-]')

    def _parse(self, decoded_content, response=None):
        soup = decoded_content

        dates = soup.select('#Platno .Datum_cas')
        names = soup.select('#Platno .Nazev')

        film_date_format = '%Y-%m-%d'

        for date, name in zip(dates, names):
            date = self._date_id_re.sub('', date['id'])
            film_date = datetime.strptime(date, film_date_format)
            film_title = name.get_text(separator='\n', strip=True)

            self._log.info(u'Scraped "{title}" from {cinema}.'.format(
                title=film_title, cinema=self.cinema_slug))
            yield ScrapedShowtime(self.cinema_slug,
                                  self._to_utc(film_date),
                                  film_title)


@active_scraper
class StarobrnoLetniKinoScraper(SoupDecoder, Scraper):
    """Scraper for Starobrno letní kino."""

    url = 'http://www.kultura-brno.cz/cs/film/starobrno-letni-kino-na-dvore-'\
        'mestskeho-divadla-brno'
    cinema_slug = 'brno-starobrno-letni-kino'
    timezone = 'Europe/Prague'

    _date_re = re.compile(r'(\d+)\.(\d+)\.')

    def _parse(self, decoded_content, response=None):
        soup = decoded_content

        for row in soup.select('.content tr'):
            cells = row.select('td')

            if len(cells) == 3:
                # date
                date = cells[1].get_text()
                match = self._date_re.search(date)
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

                self._log.info(u'Scraped "{title}" from {cinema}.'.format(
                    title=film_title, cinema=self.cinema_slug))
                yield ScrapedShowtime(self.cinema_slug,
                                      self._to_utc(film_date),
                                      film_title)


@active_scraper
class KinoLucernaScraper(SoupDecoder, Scraper):
    """Scraper for Kino Lucerna."""

    url = 'http://www.kinolucerna.info/index.php?option=com_content'\
        '&view=article&id=37&Itemid=61'
    cinema_slug = 'brno-kino-lucerna'
    timezone = 'Europe/Prague'

    _entry_re = re.compile(r'\d+:\d+')
    _entry_split_re = re.compile(r'[\b\s]+(?=\d+\.)')
    _range_re = re.compile(r'(\d+)\.(\d+)\.-(\d+)\.(\d+)\.')
    _standalone_re = re.compile(r'(\d+)\.(\d+)\.')

    def _get_date_ranges(self, dates_text):
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

    def _get_standalone_dates(self, dates_text):
        today = self.now
        dates_text = self._range_re.sub('', dates_text)
        for match in self._standalone_re.finditer(dates_text):
            month = int(match.group(2))
            year = today.year if today.month <= month else (today.year + 1)
            yield datetime(year, month, int(match.group(1)))

    def _parse(self, decoded_content, response=None):
        soup = decoded_content

        for row in soup.select('.contentpaneopen strong'):
            text = row.get_text().strip()
            match = self._entry_re.search(text)
            if match:
                text = self._entry_split_re.split(text, maxsplit=1)

                film_title = text[0].strip()
                dates_text = text[1]

                date_ranges = self._get_date_ranges(dates_text)
                standalone_dates = self._get_standalone_dates(dates_text)

                dates = list(date_ranges) + list(standalone_dates)
                for film_date in dates:
                    self._log.info(u'Scraped "{title}" from {cinema}.'.format(
                        title=film_title, cinema=self.cinema_slug))
                    yield ScrapedShowtime(self.cinema_slug,
                                          self._to_utc(film_date),
                                          film_title)


@active_scraper
class KinoArtScraper(JsonDecoder, Scraper):
    """Scraper for Kino Art."""

    _url_base = 'http://www.kinoartbrno.cz/export/?start={date}'

    url = _url_base.format(date=date.today())
    cinema_slug = 'brno-kino-art'
    timezone = 'Europe/Prague'

    def _parse(self, decoded_content, response=None):
        films = decoded_content

        film_title = ''
        film_date_format = '%Y-%m-%d %H:%M:%S'

        for film in films:
            film_date = datetime.strptime(film['datum'], film_date_format)
            film_title = film['nazevCesky']

            self._log.info(u'Scraped "{title}" from {cinema}.'.format(
                title=film_title, cinema=self.cinema_slug))
            yield ScrapedShowtime(self.cinema_slug,
                                  self._to_utc(film_date),
                                  film_title)
