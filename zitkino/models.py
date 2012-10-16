# -*- coding: utf-8 -*-


from __future__ import division

import times
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
            name=repr_name(self.__class__), cinema_slug=self.slug)


class Film(db.Document):

    _similarity_accept_ratio = 80

    id_csfd = db.IntField()
    id_imdb = db.IntField()
    id_synopsitv = db.IntField()

    _title_main = db.StringField(db_field='title_main', required=True)
    title_orig = db.StringField()
    titles = db.ListField(db.StringField())

    slug = db.StringField(required=True, unique=True)
    _year = db.IntField(db_field='year')
    length = db.IntField()

    rating_csfd = db.FloatField()
    rating_imdb = db.FloatField()
    rating_fffilm = db.FloatField()

    url_csfd = db.StringField()
    url_imdb = db.StringField()
    url_fffilm = db.StringField()
    url_synopsitv = db.StringField()

    def __init__(self, *args, **kwargs):
        self._log = logging.getLogger(__name__)
        super(Film, self).__init__(*args, **kwargs)

    @property
    def title_main(self):
        return self._title_main

    @title_main.setter
    def title_main(self, title):
        self._title_main = title
        self._create_slug()

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        self._year = year
        self._create_slug()

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

    def has_similar_title(self, title):
        """Compare two film titles by their fuzzy similarity ratio."""
        title1 = title.lower()
        result = False

        for title2 in [t.lower() for t in self.titles]:
            ratio = fuzz.partial_ratio(title1, title2)
            result = ratio >= self._similarity_accept_ratio

            op = '=' if result else '!='
            self._log.info(u'Title "%s" %s "%s" (%d%%).',
                           title1, op, title2, ratio)

            if result:
                break
        return result

    def sync(self, film):
        self.id_csfd = self.id_csfd or film.id_csfd
        self.id_imdb = self.id_imdb or film.id_imdb
        self.id_synopsitv = self.id_synopsitv or film.id_synopsitv

        self.title_main = film.title_main or self.title_main
        self.title_orig = film.title_orig or self.title_orig
        self.titles = list(set(self.titles + film.titles))

        self.year = self.year or film.year
        self.length = self.length or film.length

        self.rating_csfd = film.rating_csfd or self.rating_csfd
        self.rating_imdb = film.rating_imdb or self.rating_imdb
        self.rating_fffilm = film.rating_fffilm or self.rating_fffilm

        self.url_csfd = self.url_csfd or film.url_csfd
        self.url_imdb = self.url_imdb or film.url_imdb
        self.url_fffilm = self.url_fffilm or film.url_fffilm
        self.url_synopsitv = self.url_synopsitv or film.url_synopsitv

    def _create_slug(self):
        if self.year:
            self.slug = '{0}-{1}'.format(
                slugify(self.title_main), self.year)
        else:
            self.slug = slugify(self.title_main)

    def __repr__(self):
        return '<{name} {slug}>'.format(
            name=repr_name(self.__class__), slug=self.slug)


class Showtime(db.Document):

    cinema = db.ReferenceField(Cinema, dbref=False)
    film = db.ReferenceField(Film, dbref=False)
    starts_at = db.DateTimeField(unique_with=('cinema', 'film'))
    tags = db.ListField(db.StringField())  # dubbing, 3D, etc.

    meta = {
        'ordering': ['-starts_at']
    }

    @property
    def starts_at_day(self):
        return self.starts_at.date()

    def __repr__(self):
        return '<{name} {film!r}@{cinema!r}, {starts_at}>'.format(
            name=repr_name(self.__class__), cinema=self.cinema,
            starts_at=self.starts_at, film=self.film)


class Action(db.Document):

    name = db.StringField()
    _started_at = db.DateTimeField(db_field='started_at')
    _finished_at = db.DateTimeField(db_field='finished_at')

    @property
    def started_at_day(self):
        return self.started_at.date()

    @property
    def started_at(self):
        return self._started_at

    def start(self):
        self._started_at = times.now()

    @property
    def finished_at(self):
        return self._started_at

    def finish(self):
        self._finished_at = times.now()

    meta = {
        'ordering': ['-started_at']
    }


class LogRecord(db.Document):

    action = db.ReferenceField(Action, dbref=False)
    level = db.StringField()
    happened_at = db.DateTimeField()
    message = db.StringField()
    context = db.DictField()

    @property
    def happened_at_day(self):
        return self.happened_at.date()

    meta = {
        'ordering': ['-happened_at']
    }


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
