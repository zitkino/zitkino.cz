# -*- coding: utf-8 -*-


from __future__ import division

from datetime import timedelta

import times
from requests import RequestException

from . import db
from .image import Image
from .utils import slugify


class Cinema(db.Document):

    slug = db.StringField(required=True, unique=True)
    name = db.StringField(required=True)
    url = db.URLField()

    street = db.StringField()
    town = db.StringField(required=True)
    _coords = db.PointField(db_field='coords')

    is_exclusive = db.BooleanField(default=False)
    is_multiplex = db.BooleanField(default=False)

    @property
    def coords(self):
        return self._coords.get('coordinates', None)

    @coords.setter
    def coords(self, value):
        self._coords = value

    @property
    def priority(self):
        """Priority of this cinema. Lower is better."""
        if self.is_exclusive:
            return 1
        if self.is_multiplex:
            return 3
        return 2

    def clean(self):
        self.slug = slugify(self.name)

    def sync(self, cinema):
        """Synchronize data with other cinema object."""
        if cinema is None:
            return
        self.id = cinema.id

    def __unicode__(self):
        return u'{}'.format(self.name)


class FilmMixin(object):

    meta = {'abstract': True}

    url_csfd = db.URLField()
    url_imdb = db.URLField()

    title_main = db.StringField(required=True)
    titles = db.ListField(db.StringField())

    year = db.IntField(min_value=1877, max_value=times.now().year + 10)
    directors = db.ListField(db.StringField())
    length = db.IntField(min_value=0)

    url_poster = db.URLField()
    url_trailer = db.URLField()

    @property
    def length_hours(self):
        if self.length:
            return round(self.length / 60, 1)
        return None

    def clean(self):
        self.titles = (
            [self.title_main] +
            list(set(t for t in self.titles if t != self.title_main))
        )
        self.directors = list(frozenset(self.directors))

    def __unicode__(self):
        if self.year:
            return u'{} ({})'.format(self.title_main, self.year)
        return u'{}'.format(self.title_main)


class Film(FilmMixin, db.Document):

    is_ghost = db.BooleanField(required=True, default=False)

    slug = db.StringField(required=True, unique=True)
    year = db.IntField(min_value=1877, max_value=times.now().year + 10)

    # rating as percentage
    rating_csfd = db.IntField(min_value=0, max_value=100)
    rating_imdb = db.IntField(min_value=0, max_value=100)

    url_synopsitv = db.URLField()

    @property
    def rating(self):
        """Overall rating as percentage."""
        ratings = []
        if self.rating_csfd is not None:
            ratings.append(self.rating_csfd)
        if self.rating_imdb is not None:
            ratings.append(self.rating_imdb)
        if not ratings:
            return None
        return int(round(sum(ratings) / len(ratings), 0))

    @property
    def showtimes(self):
        return Showtime.objects.filter(film=self)

    def clean(self):
        super(Film, self).clean()
        if not self.is_ghost and not self.year:
            raise db.ValidationError(
                'Only ghost films can be without release year.'
            )
        if self.year:
            self.slug = slugify(self.title_main + '-' + str(self.year))
        else:
            self.slug = slugify(self.title_main)

    def save_overwrite(self):
        """Insert or update, depending on unique fields."""
        cls = self.__class__  # model class

        # prepare data as in save
        self.clean()

        # get all unique fields
        unique_fields = {}
        for key in self._data.keys():
            if hasattr(cls, key):  # (in case of changes in model)
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
            if hasattr(cls, key):  # (in case of changes in model)
                data['set__' + key] = value
        del data['set__id']

        # perform upsert
        query.update_one(upsert=True, **data)

        # set id (not very atomic...)
        self.id = cls.objects.get(**unique_fields).id

    def sync(self, film):
        """Synchronize data with other film object."""
        if film is None:
            return

        blacklist = [
            'id', 'slug', 'directors', 'titles', 'title_main', 'url_poster',
            'is_ghost',
        ]
        for key in self._data.keys():
            if key not in blacklist:
                val = getattr(film, key, None)
                if val is not None:
                    setattr(self, key, val)  # update

        # special cases
        self.titles.append(film.title_main)
        self.titles.extend(film.titles)
        self.directors.extend(film.directors)

        if self._is_larger_poster(film.url_poster):
            self.url_poster = film.url_poster

    def _is_larger_poster(self, url):
        """Decides whether given poster URL *url* points to an image which
        is larger than the one represented by already present poster URL.
        """
        if not url:
            return False
        if not self.url_poster:
            return True
        try:
            size1 = Image.from_url(self.url_poster).size
            size2 = Image.from_url(url).size
        except RequestException:
            return False
        return (size1[0] * size1[1]) < (size2[0] * size2[1])  # compare areas

    def __unicode__(self):
        s = self.title_main
        if self.year:
            s = s + ' ({})'.format(self.year)
        if self.is_ghost:
            s = s + ' [ghost]'
        return s


class ScrapedFilm(FilmMixin, db.EmbeddedDocument):
    """Raw representation of film as it was scraped."""

    title_scraped = db.StringField(required=True)

    def clean(self):
        title = self.title_scraped or self.title_main

        if len(title) > 3 and title.isupper():
            title_normalized = title.capitalize()
            main_titles = [title_normalized, title]
        else:
            title_normalized = title
            main_titles = [title]

        self.title_main = title_normalized
        self.title_scraped = title

        super(ScrapedFilm, self).clean()

        self.titles = (
            main_titles +
            list(set(t for t in self.titles if t not in main_titles))
        )

    def to_ghost(self):
        film = Film(
            is_ghost=True,
            title_main=self.title_main,
        )
        film.sync(self)
        return film

    def __eq__(self, other):
        if isinstance(other, ScrapedFilm):
            return self.title_scraped == other.title_scraped
        return False

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        return hash(ScrapedFilm) ^ hash(self.title_scraped)


class Showtime(db.Document):

    meta = {'ordering': ['-starts_at']}

    cinema = db.ReferenceField(Cinema, dbref=False, required=True)
    film = db.ReferenceField(Film, dbref=False, reverse_delete_rule=db.DENY)
    film_scraped = db.EmbeddedDocumentField(ScrapedFilm, required=True)
    starts_at = db.DateTimeField(required=True)
    tags = db.ListField(db.StringField())  # dubbing, 3D, etc.
    url_booking = db.URLField()
    scraped_at = db.DateTimeField(required=True, default=lambda: times.now())

    @property
    def is_paired(self):
        return self.film and not self.film.is_ghost

    @property
    def starts_at_day(self):
        return self.starts_at.date()

    @db.queryset_manager
    def upcoming(cls, queryset):
        now = times.now()
        week_later = now + timedelta(days=7)
        return (
            queryset.filter(starts_at__gte=now)
                    .filter(starts_at__lte=week_later)
                    .order_by('starts_at')
        )

    @classmethod
    def unpaired(cls):
        return (s for s in cls.objects.all() if not s.is_paired)

    def clean(self):
        self.tags = tuple(frozenset(tag for tag in self.tags if tag))

    def __unicode__(self):
        return u'{} | {} | {}'.format(
            self.starts_at,
            self.cinema.name,
            self.film_scraped.title_scraped
        )
