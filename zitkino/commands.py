# -*- coding: utf-8 -*-


import logging

import times
from flask.ext.script import Manager, Command

from .models import Cinema, Showtime
from . import __version__ as version
from .scrapers import scrapers, cinemas


class Version(Command):
    """Print version."""

    def run(self):
        print version


class SyncCinemas(Command):
    """Sync cinemas."""

    def _log_cinema(self, msg, cinema):
        logging.info(u"%s: %s", msg, cinema.slug)

    def _sync_cinema(self, cinema):
        found = Cinema.objects.with_slug(cinema.slug).first()
        if found:
            cinema.id = found.id
            self._log_cinema('Update', cinema)
        else:
            self._log_cinema('Insert', cinema)
        cinema.save()

    def run(self):
        for cinema in cinemas:
            self._sync_cinema(cinema)


class SyncShowtimes(Command):
    """Sync showtimes."""

    def _log_showtime(self, msg, showtime):
        logging.info(
            msg + u": %s | %s | %s",
            showtime.starts_at,
            showtime.cinema.name,
            showtime.film.title_main,
        )

    def _sync_showtime(self, showtime):
        if showtime.starts_at >= times.now():
            self._log_showtime('OK', showtime)
            showtime.save()
        else:
            self._log_showtime('Skipping', showtime)

    def _scrape(self):
        for scraper in scrapers:
            logging.info(u"Scraper: %s", scraper.__module__)
            results = scraper()
            if results:
                for showtime in results:
                    self._sync_showtime(showtime)

    def run(self):
        now = times.now()
        self._scrape()
        logging.info('Deleting obsolete showtimes.')
        Showtime.objects(scraped_at__lt=now).delete()


class SyncAll(Command):
    """Sync all."""

    def run(self):
        SyncCinemas().run()
        SyncShowtimes().run()


sync = Manager(usage="Run synchronizations.")
sync.add_command('cinemas', SyncCinemas())
sync.add_command('showtimes', SyncShowtimes())
sync.add_command('all', SyncAll())
