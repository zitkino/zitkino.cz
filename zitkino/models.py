# -*- coding: utf-8 -*-


from __future__ import division

from datetime import timedelta

import times

from . import db


class Cinema(db.SlugMixin, db.Document):

    meta = {'slug': ['town', 'name']}

    name = db.StringField(required=True)
    url = db.URLField()

    street = db.StringField()
    town = db.StringField(required=True)
    _coords = db.PointField(db_field='coords')

    @property
    def coords(self):
        return self._coords.get('coordinates', None)

    @coords.setter
    def coords(self, value):
        self._coords = value


class FilmMixin(object):

    meta = {'abstract': True}

    url_csfd = db.URLField()
    url_imdb = db.URLField()

    title_main = db.StringField(required=True)
    title_orig = db.StringField()
    titles = db.ListField(db.StringField())

    year = db.IntField()
    directors = db.ListField(db.StringField())
    length = db.IntField()

    @property
    def length_hours(self):
        if self.length:
            return round(self.length / 60, 1)
        return None


class Film(db.SlugMixin, FilmMixin, db.Document):

    meta = {'slug': ['title_main', 'year']}

    year = db.IntField(required=True)

    rating_csfd = db.FloatField()
    rating_imdb = db.FloatField()
    rating_fffilm = db.FloatField()

    url_fffilm = db.URLField()
    url_synopsitv = db.URLField()

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


class ScrapedFilm(FilmMixin, db.EmbeddedDocument):
    """Raw representation of film as it was scraped."""
    pass


class Showtime(db.Document):

    meta = {'ordering': ['-starts_at']}

    cinema = db.ReferenceField(Cinema, dbref=False, required=True)
    film_paired = db.ReferenceField(Film, dbref=False)
    film_scraped = db.EmbeddedDocumentField(ScrapedFilm, required=True)
    starts_at = db.DateTimeField(required=True)
    tags = db.ListField(db.StringField())  # dubbing, 3D, etc.
    url_booking = db.URLField()
    price = db.DecimalField()
    prices = db.MapField(db.DecimalField())
    scraped_at = db.DateTimeField(required=True, default=lambda: times.now())

    @property
    def starts_at_day(self):
        return self.starts_at.date()

    @property
    def film(self):
        return self.film_paired or self.film_scraped

    @db.queryset_manager
    def upcoming(cls, queryset):
        now = times.now()
        week_later = now + timedelta(days=7)
        return (
            queryset.filter(starts_at__gte=now)
                    .filter(starts_at__lte=week_later)
                    .order_by('starts_at')
        )

    def clean(self):
        self.tags = tuple(frozenset(tag for tag in self.tags if tag))
        super(Showtime, self).clean()
