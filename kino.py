# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from dateutil import rrule
from jinja2 import Environment, FileSystemLoader


films = []


# art
response = requests.get('http://www.kinoartbrno.cz/')
if response.ok:
    html = BeautifulSoup(re.sub(r'\s+', ' ', response.content))
    rows = html.select('#program_art tr')

    film_date = None

    for row in rows:
        if row.select('.datum'):
            match = re.search(r'(\d+)\. (\d+)\. (\d+)', row.get_text())
            film_date = datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
        else:
            match = re.search(r'^ *(\d+)\.(\d+) *(.+) *$', row.get_text())
            film_title = match.group(3).strip().upper()

            films.append(
                {'cinema': u'Art', 'date': film_date, 'name': film_title}
            )


# lucerna
response = requests.get('http://www.kinolucerna.info/index.php?option=com_content&view=article&id=37&Itemid=61')
if response.ok:
    html = BeautifulSoup(response.content)
    rows = html.select('.contentpaneopen strong')

    for row in rows:
        text = row.get_text().strip()
        match = re.search(r'\d+:\d+', text)
        if match:
            text = re.split(r'[\b\s]+(?=\d)', text, maxsplit=1)
            film_title = text[0].strip().upper()

            dates_text = text[1]
            re_range = re.compile(r'(\d+)\.(\d+)\.-(\d+)\.(\d+)\.')
            dates = []

            today = datetime.now()

            # ranges
            for match in re_range.finditer(dates_text):
                start_day = int(match.group(1))
                end_day = int(match.group(3))

                start_month = int(match.group(2))
                end_month = int(match.group(4))

                start_year = today.year if today.month <= start_month else (today.year + 1)
                end_year = today.year if today.month <= end_month else (today.year + 1)

                start = datetime(start_year, start_month, start_day)
                end = datetime(end_year, end_month, end_day)

                for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                    dates.append(day)

            # standalone dates
            dates_text = re_range.sub('', dates_text) # purge ranges
            for match in re.finditer(r'(\d+)\.(\d+)\.', dates_text):
                month = int(match.group(2))
                year = today.year if today.month <= month else (today.year + 1)
                dates.append(
                    datetime(year, month, int(match.group(1)))
                )

            for film_date in dates:
                films.append(
                    {'cinema': u'Lucerna', 'date': film_date, 'name': film_title}
                )


# dobrak
response = requests.get('http://kinonadobraku.cz/')
if response.ok:
    html = BeautifulSoup(re.sub(r'\s+', ' ', response.content))

    dates = html.select('#Platno .Datum_cas')
    names = html.select('#Platno .Nazev')

    for date, name in zip(dates, names):
        date = re.sub(r'[^\d\-]', '', date['id'])
        film_date = datetime.strptime(date, '%Y-%m-%d')
        film_title = name.get_text().strip().upper()

        films.append(
            {'cinema': u'Dobrák', 'date': film_date, 'name': film_title}
        )


films = sorted(films, key=lambda film: film['date'])


env = Environment(loader=FileSystemLoader('.'))
env.filters['format_date'] = lambda dt: dt.strftime('%d. %m.')

template = env.get_template('kino.html')
print template.render(films=films).encode('utf8')
