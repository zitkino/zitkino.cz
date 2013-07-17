# -*- coding: utf-8 -*-


import inspect

from zitkino.models import Cinema


class ScraperRepository(dict):

    def register(self, cinema):
        """Decorator, registers any callable as a scraper. Takes also classes
        - those are instantiated and resulting objects are taken as callables
        (assuming they have ``__call__`` method).
        """
        # create/update cinema object
        # (happens on import time, slug check prevents objects
        # to be updated multiple times)
        cinema.clean()
        if cinema.slug not in self:
            found = Cinema.objects.filter(slug=cinema.slug).first()
            if found:
                cinema.id = found.id
            cinema.save()

        def decorator(fn_or_cls):
            if inspect.isclass(fn_or_cls):
                # is it already present in repository?
                # (this prevents classes to be summoned multiple times)
                if [s for s in self.values() if s.__class__ == fn_or_cls]:
                    return fn_or_cls
                # assuming __call__
                self[cinema.slug] = fn_or_cls()
            else:
                # plain function
                self[cinema.slug] = fn_or_cls
            return fn_or_cls
        return decorator


scrapers = ScraperRepository()


# import all scrapers and let decorators do their job
from . import (  # NOQA
    kino_art,
    kino_lucerna,
    letni_kino_na_dobraku,
    rwe_letni_kino_na_riviere,
)
