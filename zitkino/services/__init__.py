# -*- coding: utf-8 -*-


class FilmDataService(object):
    """Film data service."""

    name = None

    def search(self, title, year=None):
        """Find a film by guessing."""
        raise NotImplementedError

    def lookup(self, key):
        """Find a film by ID or URL lookup."""
        raise NotImplementedError

    def lookup_obj(self, film):
        """Find a film by :class:`~zitkino.models.Film` object."""
        raise NotImplementedError


from .csfd import CSFDService
# from .imdb import IMDbService
# from .fffilm import FFFilmService
# from .synopsitv import SynopsiTVService


def pair(film):
    service = CSFDService()
    if film.url_csfd:
        service.lookup(film.url_csfd)
    return service.search(film.title_normalized, film.year)


services = [
    CSFDService(),
]
