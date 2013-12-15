# -*- coding: utf-8 -*-


from fuzzywuzzy import fuzz


from zitkino.log import pass_on_exception


class BaseFilmID(unicode):
    """Film's ID."""

    url_re = None
    url_re_group = 1

    @classmethod
    def from_url(cls, url):
        match = cls.url_re.search(url)
        if not match:
            raise ValueError
        return match.group(cls.url_re_group)


class BaseFilmService(object):
    """Film data service."""

    name = None
    url_attr = None

    min_similarity_ratio = 90

    def _match_names(self, name1, name2):
        return fuzz.ratio(name1, name2) >= self.min_similarity_ratio

    def search(self, titles, year=None, directors=None):
        """Find a film by guessing."""
        raise NotImplementedError

    def lookup(self, url):
        """Find a film by URL lookup."""
        raise NotImplementedError

    def lookup_obj(self, film):
        """Find a film by :class:`~zitkino.models.Film` object."""
        if self.url_attr:
            url = getattr(film, self.url_attr, None)
            if url:
                return self.lookup(url)
        return self.search(film.titles,
                           year=film.year, directors=film.directors)


from .database import DatabaseFilmService
from .csfd import CsfdFilmService
from .imdb import ImdbFilmService
from .synopsitv import SynopsitvFilmService


services = [
    DatabaseFilmService(),
    CsfdFilmService(),
    ImdbFilmService(),
    SynopsitvFilmService(),
]


def search(film, exclude=None):
    exclude = exclude or []
    for service in services:
        if service.__class__ not in exclude:
            with pass_on_exception():
                try:
                    match = service.lookup_obj(film)
                    if match:
                        yield match
                except NotImplementedError:
                    pass


def pair(*args, **kwargs):
    try:
        return next(search(*args, **kwargs))
    except StopIteration:
        return None
