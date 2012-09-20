# -*- coding: utf-8 -*-


from __future__ import division

import logging
from fuzzywuzzy import fuzz

from zitkino import db
from zitkino.utils import slugify, repr_name


class Cinema(db.Document):

    name = db.StringField(required=True)
    url = db.StringField()
    slug = db.StringField(required=True, unique=True)

    street = db.StringField()
    town = db.StringField()
    coords = db.GeoPointField()

    def create_slug(self):
        self.slug = '{0}-{1}'.format(
            slugify(self.town), slugify(self.name))

    def __repr__(self):
        return '<{name} {cinema_slug}>'.format(
            name=repr_name(self.__class__), cinema_slug=self.cinema_slug)


class Showtime(db.EmbeddedDocument):

    cinema = db.ReferenceField(Cinema, dbref=False)
    starts_at = db.DateTimeField(unique_with=cinema)
    tags = db.ListField(db.StringField())  # dubbing, 3D, etc.

    meta = {
        'ordering': ['-starts_at']
    }

    def __repr__(self):
        return '<{name} {cinema!r}, {starts_at}>'.format(
            name=repr_name(self.__class__), cinema=self.cinema,
            starts_at=self.starts_at)


class Film(db.Document):

    _similarity_accept_ratio = 80

    id_csfd = db.IntField(unique=True)
    id_imdb = db.IntField(unique=True)
    id_synopsitv = db.IntField(unique=True)

    title_main = db.StringField(required=True)
    title_orig = db.StringField()
    titles = db.ListField(db.StringField())

    slug = db.StringField(required=True, unique=True)
    year = db.IntField()
    length = db.IntField()

    rating_csfd = db.FloatField()
    rating_imdb = db.FloatField()
    rating_fffilm = db.FloatField()

    url_csfd = db.StringField(unique=True)
    url_imdb = db.StringField(unique=True)
    url_fffilm = db.StringField(unique=True)
    url_synopsitv = db.StringField(unique=True)

    showtimes = db.ListField(db.EmbeddedDocumentField(Showtime))

    def __init__(self, *args, **kwargs):
        self._log = logging.getLogger(__name__)
        super(Film, self).__init__(*args, **kwargs)

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

    def is_similar(self, title):
        """Compare two film titles by their fuzzy similarity ratio."""
        title1 = title.lower()
        result = False

        for title2 in [t.lower() for t in self.titles]:
            ratio = fuzz.partial_ratio(title1, title2)
            result = ratio >= self._similarity_accept_ratio

            op = '=' if result else '!='
            self._log.debug(
                u'Title "{title1}" {op} "{title2}" ({ratio}%).'.format(
                    op=op, ratio=ratio, title1=title1, title2=title2))

            if result:
                break
        return result

    def create_slug(self):
        self.slug = '{0}-{1}'.format(
            slugify(self.title_main), self.year)

    def __repr__(self):
        return '<{name} {slug} ({title!r}, {year})>'.format(
            name=repr_name(self.__class__), slug=self.slug,
            title=self.title_main, year=self.year)


data = [
    Cinema(
        name=u'Letní kino Na Dobráku',
        url='http://kinonadobraku.cz',
        slug='brno-letni-kino-na-dobraku',
        street=u'Dobrovského 29',
        town=u'Brno',
        coords=(49.2181389, 16.5888692)
    ),
    Cinema(
        name=u'Starobrno letní kino',
        url='http://www.letnikinobrno.cz',
        slug='brno-starobrno-letni-kino',
        street=u'Lidická 12',
        town=u'Brno',
        coords=(49.2013969, 16.6077600)
    ),
    Cinema(
        name=u'Kino Lucerna',
        url='http://www.kinolucerna.info',
        slug='brno-kino-lucerna',
        street=u'Minská 19',
        town=u'Brno',
        coords=(49.2104939, 16.5855358)
    ),
    Cinema(
        name=u'Kino Art',
        url='http://www.kinoartbrno.cz',
        slug='brno-kino-art',
        street=u'Cihlářská 19',
        town=u'Brno',
        coords=(49.2043861, 16.6034708)
    ),
]
