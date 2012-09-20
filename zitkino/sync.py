# -*- coding: utf-8 -*-


import times
import itertools

from zitkino.scrapers.cinemas import active_scrapers
from zitkino.scrapers.films import CSFDFilmRecognizer
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
        r = CSFDFilmRecognizer(self.user_agent)

        for showtime in self._scrape_showtimes():
            film = r.scrape(showtime)
            print repr(film)
            if film:
                print vars(film)

        # pokud najdu film podle nejakeho znaku (csfd id, title a rok, ...),
        # tak ho vratim z databaze

        # pokud ten film ma nejaka pole jako None, zkusim jej aktualizovat

        # pokud ho v databazi nenajdu, hledam ho na csfd a to mi vrati film
        # nebo None

        # pokud vrati film, ulozim ho do db a udelam test jestli ma nejaka pole
        # None, pripadne aktualizuji

        # pokud mi hledani v csfd nic nevrati, musim si film ulozit do db nejak
        # sam z informaci, ktere jsem nascrapoval v kine

        # ulozim k nemu patricna showtimes (ulozim nebo updatnu, ...)


        # sorted_films = sorted(films, key=lambda film: film.date)
        # filtered_films = [f for f in sorted_films if f.date >= self.today]
        # return filtered_films

        # TODO
        # - vyresit "čas probuzení" = "čas" ... stahovat z kin vic informaci
        #   o filmech!
