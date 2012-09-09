# -*- coding: utf-8 -*-


from __future__ import division
from datetime import datetime
from flask.ext import mongokit

from zitkino import db


class Document(mongokit.Document):
    use_dot_notation = True
    dot_notation_warning = True
    use_autorefs = True


class Cinema(Document):
    __collection__ = 'cinemas'

    structure = {
        'name': unicode,
        'url': str,
        'slug': str,
        'street': unicode,
        'town': unicode,
        'coords': (float, float),
    }
    required_fields = ['name', 'slug']
    indexes = [
        {'fields': ['slug'], 'unique': True},
        {'fields': [('coords', '2d')]},
    ]


class Film(Document):
    __collection__ = 'films'

    structure = {
        'id_csfd': int,
        'id_imdb': int,
        'id_synopsitv': int,
        'title': unicode,
        'slug': str,
        'year': int,
        'length': int,
        'rating_csfd': float,
        'rating_imdb': float,
        'rating_fffilm': float,
        'url_csfd': str,
        'url_imdb': str,
        'url_fffilm': str,
        'url_synopsitv': str,
        'showtimes': [{
            'cinema': Cinema,
            'starts_at': datetime,
        }],
    }
    i18n = ['title']
    required_fields = ['title', 'slug']
    indexes = [
        {'fields': ['title', 'year'], 'unique': True},
        {'fields': ['slug'], 'unique': True},
        {'fields': [('showtimes.starts_at', -1)]},
    ]

    @property
    def length_hours(self):
        return round(self.length / 60, 1)

    @property
    def rating(self):
        ratings = []
        if self.rating_csfd:
            ratings.append(self.rating_csfd)
        if self.rating_imdb:
            ratings.append(self.rating_imdb)
        if self.rating_fffilm:
            ratings.append(self.rating_fffilm)
        return round(sum(ratings) / len(ratings), 0)


db.register([Cinema, Film])
