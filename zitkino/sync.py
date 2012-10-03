# -*- coding: utf-8 -*-


import times
import logging
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
        self._log = logging.getLogger(__name__)
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
            showtime_title = showtime.film_title
            self._log.debug('Syncing showtime {0!r}.'.format(showtime))

            film = self._find_film_db(showtime)
            if not film:
                self._log.info('Film {0!r} not found in db.'.format(
                    showtime_title))
                film = self._find_film_csfd(showtime)
                if film:
                    self._log.info('Film {0!r} found on CSFD as {1!r}.'.format(
                        showtime_title, film.title_main))
                    film.titles.append(showtime.film_title)
                    film = self._sync_film(film)
                    self._log.info('Film {0!r} updated.'.format(film.slug))
                else:
                    self._log.info('Film {0!r} unknown.'.format(
                        showtime_title))
            else:
                self._log.info('Film {0!r} found in db.'.format(
                    showtime_title))

        # pokud ten film ma nejaka pole jako None, zkusim jej aktualizovat
        # podle toho co mam z kina

        # pokud mi hledani v csfd nic nevrati, musim si film ulozit do db nejak
        # sam z informaci, ktere jsem nascrapoval v kine

        # ulozim k nemu patricna showtimes (ulozim nebo updatnu, ...)


        # sorted_films = sorted(films, key=lambda film: film.date)
        # filtered_films = [f for f in sorted_films if f.date >= self.today]
        # return filtered_films

        # TODO
        # - vyresit "čas probuzení" = "čas" ... stahovat z kin vic informaci
        #   o filmech!
