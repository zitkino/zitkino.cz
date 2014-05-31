# -*- coding: utf-8 -*-


from __future__ import division

from hashlib import sha1
from datetime import timedelta
from collections import OrderedDict

try:
    from cStringIO import cStringIO as StringIO
except ImportError:
    from StringIO import StringIO  # NOQA

import times
from PIL import Image
from unidecode import unidecode

from . import app, db
from .http import RequestException, Session
from .utils import slugify, create_thumbnail, cached_property


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

    @property
    def showtimes(self):
        return Showtime.objects.filter(cinema=self)

    @property
    def showtimes_upcoming(self):
        return Showtime.upcoming.filter(cinema=self)

    def clean(self):
        self.slug = slugify(self.name)

    def sync(self, cinema):
        """Synchronize data with other cinema object."""
        if cinema is None:
            return
        self.id = cinema.id

    def __unicode__(self):
        return u'{}'.format(self.name)


class ImageMixin(object):

    @property
    def size(self):
        return self.width, self.height

    @property
    def area(self):
        return self.width * self.height

    @property
    def is_landscape(self):
        return self.width >= self.height

    @property
    def is_portrait(self):
        return self.height >= self.width


class PosterFile(ImageMixin, db.EmbeddedDocument):

    width = db.IntField(required=True)
    height = db.IntField(required=True)
    content = db.FileField(required=True)
    etag = db.StringField(required=True)

    def __init__(self, *args, **kwargs):
        size = kwargs.pop('size', None)
        if size:
            kwargs.setdefault('width', size[0])
            kwargs.setdefault('height', size[1])
        super(PosterFile, self).__init__(*args, **kwargs)


class Poster(ImageMixin, db.EmbeddedDocument):
    """Poster representation."""

    tn_sizes = app.config['POSTER_SIZES']

    url = db.StringField(required=True)
    files = db.MapField(db.EmbeddedDocumentField(PosterFile), required=True)

    @classmethod
    def from_url(cls, url):
        image = Image.open(StringIO(Session().get(url).content))
        if image.mode != 'RGB':
            image = image.convert('RGB')

        files = {}
        for size in cls.tn_sizes:
            poster_file = PosterFile(size=size)
            poster_file.content.new_file()

            image_tn = create_thumbnail(image, size)
            image_tn.save(poster_file.content, 'JPEG', quality=100)

            poster_file.content.close()
            poster_file.etag = sha1(poster_file.content.read()).hexdigest()

            files['{}x{}'.format(*size)] = poster_file

        return cls(url=url, files=files)

    @cached_property
    def largest(self):
        return sorted(self.files.values(),
                      key=lambda x: x.area, reverse=True)[0]

    @property
    def width(self):
        return self.largest.width

    @property
    def height(self):
        return self.largest.height

    def __unicode__(self):
        return u'{} ({}x{})'.format(self.url, *self.largest.size)


class FilmMixin(object):

    meta = {'abstract': True}

    url_csfd = db.URLField()
    url_imdb = db.URLField()

    title_main = db.StringField(required=True)
    title_orig = db.StringField()
    titles_search = db.ListField(db.StringField())

    year = db.IntField(min_value=1877, max_value=times.now().year + 10)
    directors = db.ListField(db.StringField())
    length = db.IntField(min_value=0)

    url_posters = db.ListField(db.URLField())
    url_trailer = db.URLField()

    @property
    def titles(self):
        return [t for t in (self.title_main, self.title_orig) if t]

    def clean(self):
        # cleanup titles
        if self.title_main == self.title_orig:
            self.title_orig = None
        self.titles_search = list(frozenset(
            title.lower() for title in
            (self.titles + self.titles_search)
            if title
        ))

        # cleanup directors
        self.directors = list(frozenset(
            director for director in self.directors if director
        ))

    def __unicode__(self):
        if self.year:
            return u'{} ({})'.format(self.title_main, self.year)
        return u'{}'.format(self.title_main)


class Film(db.SaveOverwriteMixin, FilmMixin, db.Document):

    is_ghost = db.BooleanField(required=True, default=False)

    slug = db.StringField(required=True, unique=True)
    year = db.IntField(min_value=1877, max_value=times.now().year + 10)

    rating_csfd = db.IntField(min_value=0, max_value=100)  # rating as %
    rating_imdb = db.IntField(min_value=0, max_value=100)  # rating as %

    url_synopsitv = db.URLField()

    posters = db.ListField(db.EmbeddedDocumentField(Poster))

    @property
    def links(self):
        links = OrderedDict()

        # data sources
        if self.url_csfd is not None:
            links[u'ČSFD'] = self.url_csfd
        if self.url_imdb is not None:
            links[u'IMDb'] = self.url_imdb
        if self.url_synopsitv is not None:
            links[u'SynopsiTV'] = self.url_synopsitv

        # cinemas
        for st in self.showtimes_upcoming.filter(film_scraped__url__ne=None):
            links[st.cinema.name] = st.film_scraped.url

        return links

    @property
    def ratings(self):
        ratings = OrderedDict()
        if self.rating_csfd is not None:
            ratings[u'ČSFD'] = self.rating_csfd
        if self.rating_imdb is not None:
            ratings[u'IMDb'] = self.rating_imdb
        return ratings

    @property
    def rating(self):
        """Overall rating as percentage."""
        ratings = self.ratings
        if not ratings:
            return None
        return int(round(sum(ratings.values()) / len(ratings), 0))

    @property
    def showtimes(self):
        return Showtime.objects.filter(film=self)

    @property
    def showtimes_upcoming(self):
        return Showtime.upcoming.filter(film=self)

    def select_poster_file(self, size=None):
        if not self.posters:
            return None
        if not size:
            posters = sorted(self.posters, key=lambda x: x.area, reverse=True)
            return posters[0].largest  # the largest file of the largest poster

        width, height = size
        orientation = 'is_portrait' if height >= width else 'is_landscape'

        def key(poster):
            # bigger or True is better, because sorting is reversed
            return (
                poster.width >= width and poster.height >= height,
                getattr(poster, orientation),  # True / False
                poster.area
            )
        posters = sorted(self.posters, key=key, reverse=True)
        return posters[0].files.get('{}x{}'.format(*size))

    def clean(self):
        super(Film, self).clean()

        # slug
        if self.year:
            self.slug = slugify(self.title_main + '-' + str(self.year))
        else:
            self.slug = slugify(self.title_main)

        # posters
        urls = list(frozenset(url for url in self.url_posters if url))
        already_processed_urls = [poster.url for poster in self.posters]
        for url in urls:
            if url not in already_processed_urls:
                try:
                    self.posters.append(Poster.from_url(url))
                except RequestException:
                    pass  # the link is probably broken, nothing we can do
        self.url_posters = urls

    def sync(self, film):
        """Synchronize data with other film object."""
        if film is None:
            return
        film.clean()

        # exclude special cases and already filled attributes
        exclude = [
            'id', 'slug', 'titles_search', 'title_main', 'title_orig'
            'url_posters', 'is_ghost', 'directors',
        ]

        is_empty = lambda v: v is not False and v != 0 and not v
        attrs = (
            k for (k, v) in self._data.items()
            if (
                (k not in exclude)  # special cases
                and is_empty(v)  # value is empty
                and not is_empty(getattr(film, k, None))  # new value not empty
            )
        )

        # update missing attributes
        for attr in attrs:
            setattr(self, attr, getattr(film, attr, None))

        # special cases
        if not self.title_main or not isinstance(film, ScrapedFilm):
            self.title_main = self._select_title(
                self.title_main,
                film.title_main
            )
        self.title_orig = self._select_title(self.title_orig, film.title_orig)
        self.titles_search.extend(film.titles_search)

        if self.is_ghost and not getattr(film, 'is_ghost', True):
            self.is_ghost = False

        self.url_posters = (self.url_posters or []) + film.url_posters

        self.clean()

    def _select_title(self, title1, title2):
        """Selects more suitable title from two given.

        Chooses according to presence of diacritics. If titles are equal in
        ASCII, but differ in unicode, the one with diacritics is returned.
        """
        if not all([title1, title2]):
            return title1 or title2  # one of them is empty
        if unidecode(title1) == unidecode(title2):
            try:
                unicode(title1).encode('ascii')
            except UnicodeEncodeError:
                return title1  # title1 has diacritics
            try:
                unicode(title2).encode('ascii')
            except UnicodeEncodeError:
                return title2  # title1 does not have diacritics, title2 has
        return title1  # cannot decide, return the first one (does not matter)

    def __unicode__(self):
        s = self.title_main
        if self.year:
            s = s + ' ({})'.format(self.year)
        if self.is_ghost:
            s = s + ' [ghost]'
        return s


class ScrapedFilm(FilmMixin, db.EmbeddedDocument):
    """Raw representation of film as it was scraped."""

    title_main_scraped = db.StringField(required=True)
    title_orig_scraped = db.StringField()

    url = db.URLField()

    def _fix_case(self, title):
        if title and len(title) > 3 and title.isupper():
            return title.capitalize()
        return title

    def clean(self):
        title_main = self._fix_case(self.title_main_scraped or self.title_main)
        self.title_main = title_main

        title_orig = self._fix_case(self.title_orig_scraped or self.title_orig)
        self.title_orig = title_orig

        self.titles_search.append(self.title_main_scraped)
        self.titles_search.append(self.title_orig_scraped)

        super(ScrapedFilm, self).clean()

    def to_ghost(self):
        self.clean()
        film = Film(is_ghost=True)
        film.sync(self)
        return film

    def __eq__(self, other):
        if isinstance(other, ScrapedFilm):
            return self.title_main_scraped == other.title_main_scraped
        return False

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        return hash(ScrapedFilm) ^ hash(self.title_main_scraped)

    def __unicode__(self):
        return self.title_main_scraped


class Showtime(db.SaveOverwriteMixin, db.Document):

    meta = {'ordering': ['-starts_at']}
    upcoming_days = 7

    cinema = db.ReferenceField(Cinema, dbref=False, required=True,
                               unique_with=['film_scraped.title_main_scraped',
                                            'starts_at'])
    film = db.ReferenceField(Film, dbref=False, reverse_delete_rule=db.DENY)
    film_scraped = db.EmbeddedDocumentField(ScrapedFilm, required=True)
    starts_at = db.DateTimeField(required=True)
    url = db.URLField(required=True)
    url_booking = db.URLField()
    scraped_at = db.DateTimeField(required=True, default=lambda: times.now())
    tags = db.TagsField(default={})

    @property
    def is_paired(self):
        return self.film and not self.film.is_ghost

    @property
    def starts_at_day(self):
        return self.starts_at.date()

    @db.queryset_manager
    def upcoming(cls, queryset):
        now = times.now() - timedelta(minutes=20)
        week_later = now + timedelta(days=cls.upcoming_days)
        return (
            queryset.filter(starts_at__gte=now)
                    .filter(starts_at__lte=week_later)
                    .order_by('starts_at')
        )

    @db.queryset_manager
    def today(cls, queryset):
        today = times.now().date()
        return (
            queryset.filter(starts_at__gt=today - timedelta(days=1))
                    .filter(starts_at__lt=today + timedelta(days=1))
                    .order_by('starts_at')
        )

    @classmethod
    def unpaired(cls):
        return (s for s in cls.objects.all() if not s.is_paired)

    def __unicode__(self):
        return u'{} | {} | {}'.format(
            self.starts_at,
            self.cinema.name,
            self.film_scraped.title_main_scraped
        )
