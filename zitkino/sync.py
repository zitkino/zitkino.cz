# -*- coding: utf-8 -*-


import itertools
import times

from zitkino.scrapers.cinemas import active_scrapers
from zitkino.scrapers.films import FilmRecognizer
from zitkino.models import data


class StaticDataSynchronizer(object):
    """Inserts or updates static data defined in models."""

    def sync(self):
        """Perform synchronization."""
        for document in data:
            found = document.__class__.objects(slug=document.slug).first()
            if found:
                document.id = found.id
                document.save()  # update
            else:
                document.save()  # insert


class ShowtimesSynchronizer(object):
    """Synchronizes showtimes."""

    scrapers = active_scrapers

    def __init__(self, user_agent=None):
        self.user_agent = user_agent

    def _scrape_showtimes(self):
        now = times.now()

        showtime_lists = []
        for scraper in self.scrapers:
            s = scraper(now, self.user_agent)
            showtime_lists.append(s.scrape())
        return itertools.chain(*showtime_lists)

    def sync(self):
        """Perform synchronization."""
        r = FilmRecognizer(self.user_agent)

        for showtime in self._scrape_showtimes():
            print r.scrape(showtime.film_title)

        # sorted_films = sorted(films, key=lambda film: film.date)
        # filtered_films = [f for f in sorted_films if f.date >= self.today]
        # return filtered_films

        # TODO
        # - vyresit requiem za sen / rekviem za sen
        # - vyresit cachovani vysledku z csfd, normalizace musi vyuzit maximalne
        #   to, co se uz drive zjistovalo
        pass
