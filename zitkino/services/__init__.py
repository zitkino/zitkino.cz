# -*- coding: utf-8 -*-


class FilmDataService(object):
    """Film data service."""

    name = None
    url_attr = None

    def search(self, title, year=None):
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
        for title in film.titles:
            f = self.search(title, film.year)
            if f:
                return f
        return None


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
