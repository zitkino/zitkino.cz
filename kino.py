# -*- coding: utf-8 -*-


import re
import os
import requests
from envoy import run as cmd
from dateutil import rrule
from datetime import datetime
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader


class Film(object):

    def __init__(self, cinema, date, title):
        self.cinema = cinema
        self.date = date
        self.title = title.upper()


class Driver(object):

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

    def to_soup(self, html):
        return BeautifulSoup(re.sub(r'\s+', ' ', html))

    def parse(self, soup):
        return []

    def scrape(self):
        if not self.films:
            self.films = list(self.parse(self.to_soup(self.download())))
        return self.films


class DobrakDriver(Driver):

    url = 'http://kinonadobraku.cz/'

    def parse(self, soup):
        dates = soup.select('#Platno .Datum_cas')
        names = soup.select('#Platno .Nazev')

        for date, name in zip(dates, names):
            date = re.sub(r'[^\d\-]', '', date['id'])
            film_date = datetime.strptime(date, '%Y-%m-%d')
            film_title = name.get_text().strip().upper()

            yield Film(u'Dobrák', film_date, film_title)


class ArtDriver(Driver):

    url = 'http://www.kinoartbrno.cz/'

    def parse(self, soup):
        film_date = None

        for row in soup.select('#program_art tr'):
            if row.select('.datum'):
                match = re.search(r'(\d+)\. (\d+)\. (\d+)', row.get_text())
                film_date = datetime(
                    int(match.group(3)),
                    int(match.group(2)),
                    int(match.group(1))
                )

            else:
                match = re.search(r'^ *(\d+)\.(\d+) *(.+) *$', row.get_text())
                film_title = match.group(3).strip().upper()

                yield Film('Art', film_date, film_title)


class LucernaDriver(Driver):

    url = 'http://www.kinolucerna.info/index.php?option=com_content&view=article&id=37&Itemid=61'
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
                text = re.split(r'[\b\s]+(?=\d)', text, maxsplit=1)

                film_title = text[0].strip().upper()
                dates_text = text[1]

                date_ranges = self.get_date_ranges(dates_text)
                standalone_dates = self.get_standalone_dates(dates_text)

                dates = list(date_ranges) + list(standalone_dates)
                for film_date in dates:
                    yield Film(u'Lucerna', film_date, film_title)


class Deployer(object):

    # https://devcenter.heroku.com/articles/read-only-filesystem
    temp_dir = './tmp'
    release_file = 'kino.html'

    def __init__(self):
        self.username = os.environ.get('GITHUB_USERNAME')
        self.password = os.environ.get('GITHUB_PASSWORD')

    def deploy(self, html):
        try:
            cmd('rm -rf ' + self.temp_dir)
            cmd('mkdir ' + self.temp_dir)

            print 'Cloning git repository.'
            cmd('git clone -b gh-pages https://{0}:{1}@github.com/honzajavorek/blog.git {2}'.format(
                self.username,
                self.password,
                self.temp_dir
            ))

            print 'Writing file.'
            with open(os.path.join(self.temp_dir, self.release_file), 'w') as f:
                f.write(html)

            print 'Commiting changes.'
            os.chdir(self.temp_dir)
            cmd('git add ' + self.release_file)
            cmd('git commit -m "kino update"')

            print 'Pushing changes.'
            cmd('git push origin gh-pages')
            os.chdir('..')

            cmd('rm -rf ' + self.temp_dir)
        except Exception as e:
            print e


class Kino(object):

    drivers = (
        ArtDriver,
        DobrakDriver,
        LucernaDriver,
    )

    template_filters = {
        'format_date': lambda dt: dt.strftime('%d. %m.'),
    }

    templates_dir = '.'
    template_name = 'kino.html'

    def setup_jinja_env(self):
        jinja_env = Environment(loader=FileSystemLoader(self.templates_dir))
        jinja_env.filters.update(self.template_filters)
        return jinja_env

    def scrape_films(self):
        films = []
        for driver in self.drivers:
            films += list(driver().scrape())
        return sorted(films, key=lambda film: film.date)

    def render_template(self, films):
        jinja_env = self.setup_jinja_env()
        template = jinja_env.get_template(self.template_name)
        return template.render(
            films=films,
        ).encode('utf8')

    def run(self):
        html = self.render_template(self.scrape_films())
        Deployer().deploy(html)


if __name__ == '__main__':
    Kino().run()
