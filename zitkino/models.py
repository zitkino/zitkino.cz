# -*- coding: utf-8 -*-


from __future__ import division

from datetime import timedelta

import times

from . import db
from .utils import slugify


class Cinema(db.Document):

    slug = db.StringField(required=True, unique=True)
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

    def clean(self):
        self.slug = slugify(self.name)


class FilmMixin(object):

    meta = {'abstract': True}

    url_csfd = db.URLField()
    url_imdb = db.URLField()

    title_main = db.StringField(required=True)
    titles = db.ListField(db.StringField())

    year = db.IntField()
    directors = db.ListField(db.StringField())
    length = db.IntField()

    @property
    def title_normalized(self):
        title = self.title_main
        if len(title) > 3 and title.isupper():
            return title.capitalize()
        return title

    @property
    def length_hours(self):
        if self.length:
            return round(self.length / 60, 1)
        return None

    def sync(self):
        """Insert or update, depending on unique fields."""
        cls = self.__class__  # model class

        # prepare data as in save
        self.clean()

        # get all unique fields
        unique_fields = {}
        for key in self._data.keys():
            field = getattr(cls, key)  # field object
            if field.unique:
                unique_fields[key] = getattr(self, key)  # value
            for key in (field.unique_with or []):
                unique_fields[key] = getattr(self, key)  # value

        # select the object by its unique fields
        query = cls.objects(**unique_fields)

        # prepare data to set
        data = {}
        for key, value in self._data.items():
            data['set__' + key] = value
        del data['set__id']

        # perform upsert
        query.update_one(upsert=True, **data)

        # set id
        self.id = cls.objects.get(**unique_fields).id

    def __unicode__(self):
        if self.year:
            return u'{} ({})'.format(self.title_main, self.year)
        return u'{}'.format(self.title_main)


class Film(FilmMixin, db.Document):

    slug = db.StringField(required=True, unique=True)
    year = db.IntField(required=True)

    # rating as percentage
    rating_csfd = db.IntField(min_value=0, max_value=100)
    rating_imdb = db.IntField(min_value=0, max_value=100)
    rating_fffilm = db.IntField(min_value=0, max_value=100)

    url_fffilm = db.URLField()
    url_synopsitv = db.URLField()

    @property
    def rating(self):
        """Overall rating as percentage."""
        ratings = []
        if self.rating_csfd:
            ratings.append(self.rating_csfd)
        if self.rating_imdb:
            ratings.append(self.rating_imdb)
        if self.rating_fffilm:
            ratings.append(self.rating_fffilm)
        return round(sum(ratings) / len(ratings), 0)

    def clean(self):
        self.slug = slugify(self.title_main + '_' + str(self.year))


class ScrapedFilm(FilmMixin, db.EmbeddedDocument):
    """Raw representation of film as it was scraped."""

    def __eq__(self, other):
        if isinstance(other, ScrapedFilm):
            return self.title_main == other.title_main
        return False

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        return hash(ScrapedFilm) ^ hash(self.title_main)


class Showtime(db.Document):

    meta = {'ordering': ['-starts_at']}

    cinema = db.ReferenceField(Cinema, dbref=False, required=True)
    film_paired = db.ReferenceField(Film, dbref=False,
                                    reverse_delete_rule=db.DENY)
    film_scraped = db.EmbeddedDocumentField(ScrapedFilm, required=True)
    starts_at = db.DateTimeField(required=True)
    tags = db.ListField(db.StringField())  # dubbing, 3D, etc.
    url_booking = db.URLField()
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

    def __unicode__(self):
        return u'{} | {} | {}'.format(
            self.starts_at,
            self.cinema.name,
            self.film.title_main
        )
