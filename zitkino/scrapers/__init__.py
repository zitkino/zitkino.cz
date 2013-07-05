# -*- coding: utf-8 -*-


import inspect

from zitkino.models import Cinema


class ScraperRepository(list):

    def register(self, fn_or_cls):
        """Decorator, registers any callable as a scraper. Takes also classes
        - those are instantiated and resulting objects are taken as callables
        (assuming they have ``__call__`` method).
        """
        if inspect.isclass(fn_or_cls):
            fn = fn_or_cls()  # assuming __call__
        else:
            fn = fn_or_cls
        self.append(fn)
        return fn_or_cls


class CinemaRepository(list):

    def register(self, **kwargs):
        """Registers cinema object."""
        self.append(Cinema(**kwargs))


scrapers = ScraperRepository()
cinemas = CinemaRepository()


from . import (  # NOQA
    brno_kino_art,
    brno_kino_lucerna,
    brno_letni_kino_na_dobraku,
    brno_rwe_letni_kino_na_riviere,
)
