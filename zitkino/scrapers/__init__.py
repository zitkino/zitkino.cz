# -*- coding: utf-8 -*-


import inspect

from zitkino.models import Cinema


class ScraperRepository(set):

    def register(self, fn_or_cls):
        """Decorator, registers any callable as a scraper. Takes also classes
        - those are instantiated and resulting objects are taken as callables
        (assuming they have ``__call__`` method).
        """
        if inspect.isclass(fn_or_cls):
            if [s for s in self if s.__class__ == fn_or_cls]:
                return fn_or_cls  # already present in repository
            fn = fn_or_cls()  # assuming __call__
        else:
            fn = fn_or_cls
        self.add(fn)

        return fn_or_cls


class CinemaRepository(set):

    def register(self, **kwargs):
        """Registers cinema object."""
        cinema = Cinema(**kwargs)
        cinema.clean()

        found = [c for c in self if c.slug == cinema.slug]
        if found:
            return found[0]

        found = Cinema.objects.filter(slug=cinema.slug).first()
        if found:
            cinema.id = found.id
        cinema.save()

        self.add(cinema)
        return cinema


scrapers = ScraperRepository()
cinemas = CinemaRepository()


from . import (  # NOQA
    kino_art,
    kino_lucerna,
    letni_kino_na_dobraku,
    rwe_letni_kino_na_riviere,
)
