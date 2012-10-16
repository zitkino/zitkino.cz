#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from zitkino.utils import slugify, repr_name


class TestCase(unittest.TestCase):
    pass


class SlugifyTest(TestCase):

    def test_str(self):
        self.assertEquals(slugify('blue smurf'),
                          'blue-smurf')

    def test_unicode(self):
        self.assertEquals(slugify(u'modrý šmoulík'),
                          'modry-smoulik')

    def test_different_case(self):
        self.assertEquals(slugify(u'MoDrÝ ŠmOuLíK'),
                          'modry-smoulik')

    def test_non_alphanumeric(self):
        self.assertEquals(slugify(u'(světle) modrý šmoula'),
                          'svetle-modry-smoula')

    def test_whitespace(self):
        self.assertEquals(slugify(u'   modrý šmoula\t'),
                          'modry-smoula')


class ReprNameTest(TestCase):

    def test_self(self):
        self.assertEquals(repr_name(self.__class__),
                          'tests.test_utils.ReprNameTest')


if __name__ == '__main__':
    unittest.main()
