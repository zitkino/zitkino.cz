# -*- coding: utf-8 -*-


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

    def search(self, titles, year=None):
        """Find a film by guessing."""
        raise NotImplementedError

    def lookup(self, url):
        """Find a film by URL lookup."""
        raise NotImplementedError

    def lookup_obj(self, film):
        """Find a film by :class:`~zitkino.models.Film` object."""
        if self.url_attr:
            url = getattr(film, self.url_attr)
            if url:
                return self.lookup(url)
        return self.search(film.titles, film.year)


from .csfd import CsfdFilmService
from .imdb import ImdbFilmService
from .synopsitv import SynopsitvFilmService


def pair(film):
    service = CsfdFilmService()
    if film.url_csfd:
        service.lookup(film.url_csfd)
    return service.search(film.titles, film.year)


services = [
    CsfdFilmService(),
    ImdbFilmService(),
    SynopsitvFilmService(),
]
