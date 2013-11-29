# -*- coding: utf-8 -*-


class FilmDataService(object):
    """Film data service."""

    def search(self, title, year=None):
        """Find a film by guessing."""
        raise NotImplementedError

    def lookup(self, key):
        """Find a film by ID or URL lookup."""
        raise NotImplementedError


from .csfd import CSFDService
# from .imdb import IMDbService
# from .fffilm import FFFilmService
# from .synopsitv import SynopsiTVService


def pair(*args, **kwargs):
    return CSFDService().search(*args, **kwargs)


def update(film):
    raise NotImplementedError
