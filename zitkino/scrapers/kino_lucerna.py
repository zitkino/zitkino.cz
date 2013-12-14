# -*- coding: utf-8 -*-


import re
from collections import namedtuple
from datetime import datetime, date, time

import times
from dateutil import rrule

from zitkino import http
from zitkino import parsers
from zitkino.utils import clean_whitespace
from zitkino.models import Cinema, Showtime, ScrapedFilm

from zitkino.scrapers import scrapers


cinema = Cinema(
    name=u'Kino Lucerna',
    url='http://www.kinolucerna.info',
    street=u'Minská 19',
    town=u'Brno',
    coords=(49.2104939, 16.5855358)
)


FilmInfo = namedtuple('FilmInfo', ['title_main', 'tags', 'directors'])


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
        r'((\s+(ve?|a)\s+\d+:\d+)+)'  # times
    )
    standalone_re = re.compile(
        r'(\d+)\.(\d+)\.(\s*\+\s*(\d+)\.(\d+)\.)?'  # single dates or date+date
        r'((\s+(ve?|a)\s+\d+:\d+)+)'  # times
    )
    time_re = re.compile(r'(\d+):(\d+)')

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
        for texts in self._scrape_entries():
            for showtime in self._parse_entry_text(*texts):
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

            if next_el is None:
                return False

            # we found BR tag - does it have tail (standalone text after the
            # element) with some film details?
            return bool(next_el.tail)
        return False

    def _extract_entry_siblings_text(self, el, direction):
        text = ''
        while True:
            el = getattr(el, 'get' + direction)()
            if el is not None and el.tag == 'strong':  # continuation
                if direction != 'previous' or el.tail is None:
                    text += (el.text_content(whitespace=True) or '')
            else:
                return text

    def _extract_entry_tail_text(self, el):
        text = ''
        seen_text = False
        while True:
            next_el = el.getnext()
            if next_el is None:
                return text
            if next_el.tag == 'strong':
                if not seen_text:
                    text = next_el.tail or ''
                    el = next_el
                    continue
                else:
                    return text
            else:
                seen_text = True
                text += next_el.text_content() + ' ' + (next_el.tail or '')
                el = next_el

    def _extract_entry_text(self, entry):
        """Extracts relevant entry text from given STRONG element and it's
        siblings (sometimes film entry actually consists of multiple STRONG
        elements as someone made the text bold by selecting multiple
        parts of it and pushing the button in WYSIWYG editor).
        """
        title_text = self._extract_entry_siblings_text(entry, 'previous')
        title_text += (entry.text_content(whitespace=True) or '')
        title_text += self._extract_entry_siblings_text(entry, 'next')

        details_text = self._extract_entry_tail_text(entry)

        return title_text.strip(), clean_whitespace(details_text)

    def _scrape_entries(self):
        """Downloads and scrapes text of HTML elements, each with film
        header line.
        """
        resp = http.get(self.url)
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
        if '\n' in text:
            parts = text.split('\n')
            title = parts[0]
            for info in parts[1:]:
                dates = self.entry_split_price_re.split(info, maxsplit=1)[0]
                yield clean_whitespace(title), clean_whitespace(dates)
        else:
            title, info = self.entry_split_re.split(text, maxsplit=1)
            dates = self.entry_split_price_re.split(info, maxsplit=1)[0]
            yield clean_whitespace(title), clean_whitespace(dates)

    def _parse_info(self, title_text, details_text):
        tags = []
        directors = {}

        # tags
        for regexp, tag in self.tag_re:
            if regexp.search(title_text):
                tags.append(tag)
                title_text = regexp.sub('', title_text).strip()
            if regexp.search(details_text):
                tags.append(tag)

        # TODO directors

        return FilmInfo(title_text.strip(), tags, directors)

    def _parse_entry_text(self, title_text, details_text):
        """Takes HTML element with film header line and generates showtimes."""
        for title_text, dates_text in self._split_entry_text(title_text):
            info = self._parse_info(title_text, details_text)

            date_ranges = self._parse_date_ranges(dates_text)
            standalone_dates = self._parse_standalone_dates(dates_text)

            dates = list(date_ranges) + list(standalone_dates)
            for starts_at in dates:
                yield Showtime(
                    cinema=cinema,
                    film_scraped=ScrapedFilm(
                        title_scraped=info.title_main,
                        titles=[info.title_main],
                    ),
                    starts_at=starts_at,
                    url_booking=self.url_booking,
                    tags={tag: None for tag in info.tags},
                    directors=info.directors,
                )
