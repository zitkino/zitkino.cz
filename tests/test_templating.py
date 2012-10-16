#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import datetime

from zitkino.templating import urlencode_filter, format_date_filter,\
    format_date_ics_filter, format_timestamp_ics_filter


class TestCase(unittest.TestCase):
    pass


class UrlencodeTest(TestCase):

    def test(self):
        self.assertEquals(urlencode_filter('foo @+%/'),
                          'foo+%40%2B%25%2F')


class FormatDateTest(TestCase):

    def test(self):
        dt = datetime.datetime(2012, 8, 30, 12, 01, 42)
        self.assertEquals(format_date_filter(dt),
                          '30. 8.')


class FormatDateIcsTest(TestCase):

    def test(self):
        dt = datetime.datetime(2012, 8, 30, 12, 01, 42)
        self.assertEquals(format_date_ics_filter(dt),
                          '20120830')


class FormatTimestampIcsTest(TestCase):

    def test(self):
        dt = datetime.datetime(2012, 8, 30, 12, 01, 42)
        self.assertEquals(format_timestamp_ics_filter(dt),
                          '20120830T120142Z')


if __name__ == '__main__':
    unittest.main()
