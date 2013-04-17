# -*- coding: utf-8 -*-


from __future__ import division

from fuzzywuzzy import fuzz

from . import db
from .utils import slugify, repr_name


class Cinema(db.Document):

    _name = db.StringField(required=True, db_field='name')
    url = db.StringField()
    slug = db.StringField(required=True, unique=True)

    street = db.StringField()
    _town = db.StringField(db_field='town')
    coords = db.GeoPointField()

    def __init__(self, *args, **kwargs):
        super(Cinema, self).__init__(*args, **kwargs)
        self.slug = self._create_slug()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.slug = self._create_slug()

    @property
    def town(self):
        return self._town

    @name.setter
    def town(self, town):
        self._town = town
        self.slug = self._create_slug()

    def _create_slug(self):
        parts = filter(None, [self._town, self._name])
        return slugify(u'-'.join(parts))

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
    directors = db.ListField(db.StringField())

    rating_csfd = db.FloatField()
    rating_imdb = db.FloatField()
    rating_fffilm = db.FloatField()

    url_csfd = db.StringField()
    url_imdb = db.StringField()
    url_fffilm = db.StringField()
    url_synopsitv = db.StringField()

    def __init__(self, *args, **kwargs):
        super(Film, self).__init__(*args, **kwargs)
        self.slug = self._create_slug()

    @property
    def title_main(self):
        return self._title_main

    @title_main.setter
    def title_main(self, title):
        self._title_main = title
        self.slug = self._create_slug()

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        self._year = year
        self.slug = self._create_slug()

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
            self._log.debug(u'Title "%s" %s "%s" (%d%%).',
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
        parts = filter(None, [self._title_main, str(self._year)])
        return slugify(u'-'.join(parts))

    def __repr__(self):
        return '<{name} {slug}>'.format(
            name=repr_name(self.__class__), slug=self.slug)


class ScrapedFilm(db.EmbeddedDocument):

    id_csfd = db.IntField()
    id_imdb = db.IntField()

    titles = db.ListField(db.StringField())
    year = db.IntField()
    directors = db.ListField(db.StringField())


class Showtime(db.Document):

    cinema = db.ReferenceField(Cinema, dbref=False)
    film = db.EmbeddedDocumentField(ScrapedFilm)
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


data = [
    Cinema(
        name=u'Letní kino Na Dobráku',
        url='http://kinonadobraku.cz',
        street=u'Dobrovského 29',
        town=u'Brno',
        coords=(49.2181389, 16.5888692)
    ),
    Cinema(
        name=u'Starobrno letní kino',
        url='http://www.letnikinobrno.cz',
        street=u'Lidická 12',
        town=u'Brno',
        coords=(49.2013969, 16.6077600)
    ),
    Cinema(
        name=u'Kino Lucerna',
        url='http://www.kinolucerna.info',
        street=u'Minská 19',
        town=u'Brno',
        coords=(49.2104939, 16.5855358)
    ),
    Cinema(
        name=u'Kino Art',
        url='http://www.kinoartbrno.cz',
        street=u'Cihlářská 19',
        town=u'Brno',
        coords=(49.2043861, 16.6034708)
    ),
]
