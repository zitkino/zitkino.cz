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


def pair(title, year=None):
    return CSFDService().search(title, year)


def update(film):
    raise NotImplementedError
