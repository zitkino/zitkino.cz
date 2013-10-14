# -*- coding: utf-8 -*-


import re
from datetime import datetime, date, time

import times
from dateutil import rrule

from zitkino import parsers
from zitkino.utils import download
from zitkino.models import Cinema, Showtime, ScrapedFilm

from zitkino.scrapers import scrapers


cinema = Cinema(
    name=u'Kino Lucerna',
    url='http://www.kinolucerna.info',
    street=u'Minská 19',
    town=u'Brno',
    coords=(49.2104939, 16.5855358)
)


@scrapers.register(cinema)
class Scraper(object):

    url = ('http://www.kinolucerna.info/index.php?option=com_content'
           '&view=article&id=37&Itemid=61')
    url_booking = ('http://www.kinolucerna.info/index.php?option=com_contact'
                   '&view=contact&id=1&Itemid=63')

    tz = 'Europe/Prague'

    entry_re = re.compile(r'\d+:\d+')
    entry_split_re = re.compile(r'[\b\s]+(?=\d+\.)')
    entry_split_price_re = re.compile(ur'vstupné', re.U | re.I)

    range_re = re.compile(
        r'(\d+)\.(\d+)\.-(\d+)\.(\d+)\.'  # date range
        r'((\s+(ve?|a)\s+\d+:\d+)*)'  # times
    )
    standalone_re = re.compile(
        r'(\d+)\.(\d+)\.(\s*\+\s*(\d+)\.(\d+)\.)?'  # single dates or date+date
        r'((\s+(ve?|a)\s+\d+:\d+)*)'  # times
    )
    time_re = re.compile(r'(\d+):(\d+)')

    tag_re = (
        (re.compile(r'(?P<title>.*) *ve? *2[dD]$'), '2D'),
        (re.compile(r'(?P<title>.*) *ve? *3[dD]$'), '3D'),
    )

    def __call__(self):
        for entry_text in self._scrape_entries():
            for showtime in self._parse_entry_text(entry_text):
                yield showtime

    def _is_entry(self, el):
        """Tests if given STRONG element looks like film entry."""
        def looks_like_entry(el):
            return (
                el.tag == 'strong' and
                self.entry_re.search(el.text_content())
            )

        if looks_like_entry(el):
            next_el = el.getnext()  # get next sibling
            # let's look for the next BR tag
            while next_el is not None and next_el.tag != 'br':
                if looks_like_entry(next_el):
                    # we found another entry candidate until BR tag is found,
                    # that means examined element is probably not a film header
                    return False
                next_el = next_el.getnext()  # get next sibling

            # we found BR tag - does it have tail (standalone text after the
            # element) with some film details?
            return bool(next_el.tail)
        return False

    def _extract_entry_text(self, entry):
        """Extracts relevant entry text from given STRONG element and it's
        siblings (sometimes film entry actually consists of multiple STRONG
        elements as someone made the text bold by selecting multiple
        parts of it and pushing the button in WYSIWYG editor)."""

        def extract_siblings(el, direction):
            text = ''
            while True:
                el = getattr(el, 'get' + direction)()
                if el is not None and el.tag == 'strong':  # continuation
                    if direction != 'previous' or el.tail is None:
                        text += (el.text_content(whitespace=True) or '')
                else:
                    return text

        text = extract_siblings(entry, 'previous')
        text += (entry.text_content(whitespace=True) or '')
        text += extract_siblings(entry, 'next')
        return text.strip()

    def _scrape_entries(self):
        """Downloads and scrapes text of HTML elements, each with film
        header line.
        """
        resp = download(self.url)
        html = parsers.html(resp.content, base_url=resp.url)

        for el in html.cssselect('.contentpaneopen strong'):
            if self._is_entry(el):
                yield self._extract_entry_text(el)

    def _determine_year(self, month):
        """Determines the right year of datetime from given month."""
        tod = date.today()
        month = int(month)
        if tod.month <= month:
            # this month or future month this year
            return tod.year
        elif tod.month - month < 6:
            # looks like future month next year, but it is too far - therefore
            # it is month in the past this year, which just passed
            return tod.year
        else:
            # future month next year
            return tod.year + 1

    def _parse_times(self, times_text):
        """Takes text with time information, parses out and generates
        hour & minute pairs.
        """
        return [
            map(int, [time_match.group(1), time_match.group(2)])  # hr, min
            for time_match in self.time_re.finditer(times_text)
        ]

    def _parse_date_ranges(self, dates_text):
        """Takes text with date & time information, parses out and generates
        showtimes within date ranges.
        """
        for match in self.range_re.finditer(dates_text):
            # days
            start_day = int(match.group(1))
            end_day = int(match.group(3))

            # months
            start_month = int(match.group(2))
            end_month = int(match.group(4))

            # times
            time_args_list = self._parse_times(match.group(5))

            # years
            start_year = self._determine_year(start_month)
            end_year = self._determine_year(end_month)

            # bounds for rrule
            start = datetime(start_year, start_month, start_day)
            end = datetime(end_year, end_month, end_day)

            # construct and yield datetimes
            for day in rrule.rrule(rrule.DAILY, dtstart=start, until=end):
                for time_args in time_args_list:
                    yield times.to_universal(
                        datetime.combine(day, time(*time_args)),
                        self.tz
                    )

    def _parse_standalone_dates(self, dates_text):
        """Takes text with date & time information, parses out and generates
        standalone showtimes.
        """
        dates_text = self.range_re.sub('', dates_text)
        for match in self.standalone_re.finditer(dates_text):
            date_args_list = []

            # standalone date
            date_args_list.append(map(int, [
                self._determine_year(match.group(2)),  # year
                match.group(2),  # month
                match.group(1),  # day
            ]))

            # date+date, let's process the second one
            if match.group(3):
                date_args_list.append(map(int, [
                    self._determine_year(match.group(5)),  # year
                    match.group(5),  # month
                    match.group(4),  # day
                ]))

            # parse times
            time_args_list = self._parse_times(match.group(6))

            # construct and yield datetimes
            for date_args in date_args_list:
                for time_args in time_args_list:
                    yield times.to_universal(
                        datetime(*(date_args + time_args)),
                        self.tz
                    )

    def _split_entry_text(self, text):
        """Takes main entry text and returns tuple with title part
        and a part containing information about dates & times.
        """
        title, remainder = self.entry_split_re.split(text, maxsplit=1)
        remainder = self.entry_split_price_re.split(remainder, maxsplit=1)
        return title.strip(), remainder[0].strip()

    def _split_title_text(self, title):
        title = title.strip()
        tags = []
        matched = True
        while matched:
            matched = False
            for regex, tag in self.tag_re:
                match = regex.match(title)
                if match:
                    title = match.group('title').strip()
                    tags.append(tag)
                    matched = True
        return title, tags

    def _parse_entry_text(self, text):
        """Takes HTML element with film header line and generates showtimes."""
        title, dates_text = self._split_entry_text(text)
        title_main, tags = self._split_title_text(title)

        date_ranges = self._parse_date_ranges(dates_text)
        standalone_dates = self._parse_standalone_dates(dates_text)

        dates = list(date_ranges) + list(standalone_dates)
        for starts_at in dates:
            yield Showtime(
                cinema=cinema,
                film_scraped=ScrapedFilm(
                    title_main=title_main,
                    titles=[title_main],
                ),
                starts_at=starts_at,
                url_booking=self.url_booking,
                tags=tags,
            )
