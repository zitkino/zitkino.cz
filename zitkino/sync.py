# -*- coding: utf-8 -*-


import times
import itertools

from zitkino.scrapers.cinemas import active_scrapers
from zitkino.scrapers.films import CSFDFilmRecognizer
from zitkino.models import data, Film


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
        self.csfd_recognizer = CSFDFilmRecognizer(user_agent)

    def _scrape_showtimes(self):
        now = times.now()

        showtime_lists = []
        for scraper in self.scrapers:
            s = scraper(now, self.user_agent)
            showtime_lists.append(s.scrape())
        return itertools.chain(*showtime_lists)

    def _sync_film(self, film):
        film_db = Film.objects(slug=film.slug).first()
        if film_db:
            film_db.sync(film)
            film_db.save()
            return film_db
        film.save()
        return film

    def _find_film_db(self, showtime):
        params = {'titles__iexact': showtime.film_title}
        return Film.objects(**params).first()

    def _find_film_csfd(self, showtime):
        return self.csfd_recognizer.scrape(showtime)

    def sync(self):
        """Perform synchronization."""
        for showtime in self._scrape_showtimes():
            film = self._find_film_db(showtime)
            if film:
                print 'found'
            else:
                film = self._find_film_csfd(showtime)
                if film:
                    film.titles.append(showtime.film_title)
                    film = self._sync_film(film)
                    print 'synced to ', film.slug
                else:
                    print 'unknown'

        # pokud ten film ma nejaka pole jako None, zkusim jej aktualizovat

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
