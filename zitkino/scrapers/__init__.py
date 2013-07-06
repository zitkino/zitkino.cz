# -*- coding: utf-8 -*-


import inspect

from zitkino.models import Cinema


class ScraperRepository(dict):

    def register(self, cinema):
        """Decorator, registers any callable as a scraper. Takes also classes
        - those are instantiated and resulting objects are taken as callables
        (assuming they have ``__call__`` method).
        """
        cinema.clean()
        if cinema.slug not in self:
            found = Cinema.objects.filter(slug=cinema.slug).first()
            if found:
                cinema.id = found.id
            cinema.save()

        def decorator(fn_or_cls):
            if inspect.isclass(fn_or_cls):
                if [s for s in self if s.__class__ == fn_or_cls]:
                    return fn_or_cls  # already present in repository
                self[cinema.slug] = fn_or_cls()  # assuming __call__
            else:
                self[cinema.slug] = fn_or_cls
            return fn_or_cls
        return decorator


scrapers = ScraperRepository()


from . import (  # NOQA
    kino_art,
    kino_lucerna,
    letni_kino_na_dobraku,
    rwe_letni_kino_na_riviere,
)
