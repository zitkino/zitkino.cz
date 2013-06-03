# -*- coding: utf-8 -*-


from __future__ import division

from . import db


class Cinema(db.SlugMixin, db.Document):

    meta = {
        'slug': ['town', 'name'],
    }

    name = db.StringField(required=True)
    url = db.StringField()

    street = db.StringField()
    town = db.StringField(required=True)
    _coords = db.PointField(db_field='coords')

    @property
    def coords(self):
        return self._coords.get('coordinates', None)

    @coords.setter
    def coords(self, value):
        self._coords = value


class Film(db.SlugMixin, db.Document):

    meta = {
        'slug': ['title_main', 'year'],
    }

    id_csfd = db.IntField()
    id_imdb = db.IntField()
    id_synopsitv = db.IntField()

    title_main = db.StringField(required=True)
    title_orig = db.StringField()
    titles = db.ListField(db.StringField())

    year = db.IntField(required=True)
    length = db.IntField()
    directors = db.ListField(db.StringField())

    rating_csfd = db.FloatField()
    rating_imdb = db.FloatField()
    rating_fffilm = db.FloatField()

    url_csfd = db.StringField()
    url_imdb = db.StringField()
    url_fffilm = db.StringField()
    url_synopsitv = db.StringField()

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


class ScrapedFilm(db.EmbeddedDocument):
    """Raw representation of film as it was scraped."""

    id_csfd = db.IntField()
    id_imdb = db.IntField()

    titles = db.ListField(db.StringField())
    year = db.IntField()
    directors = db.ListField(db.StringField())


class Showtime(db.Document):

    meta = {
        'ordering': ['-starts_at'],
    }

    cinema = db.ReferenceField(Cinema, dbref=False)
    film = db.EmbeddedDocumentField(ScrapedFilm)
    starts_at = db.DateTimeField(unique_with=('cinema', 'film'))
    tags = db.ListField(db.StringField())  # dubbing, 3D, etc.

    @property
    def starts_at_day(self):
        return self.starts_at.date()

    def __repr__(self):
        return '<{name} {film!r}@{cinema!r}, {starts_at}>'.format(
            name=self._repr_name(), cinema=self.cinema,
            starts_at=self.starts_at, film=self.film)


### Static data


static_data = [
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
