# -*- coding: utf-8 -*-


import logging

import times
from flask.ext.script import Manager, Command

from .models import Showtime
from .scrapers import scrapers
from . import __version__ as version


class Version(Command):
    """Print version."""

    def run(self):
        print version


class SyncShowtimes(Command):
    """Sync showtimes."""

    def _log_showtime(self, showtime, msg='Showtime'):
        logging.info(
            msg + u": %s | %s | %s",
            showtime.starts_at,
            showtime.cinema.name,
            showtime.film.title_main,
        )

    def _sync_showtime(self, showtime):
        if showtime.starts_at >= times.now():
            self._log_showtime(showtime)
            showtime.save()
        else:
            self._log_showtime(showtime, 'Past showtime')

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
        SyncShowtimes().run()


sync = Manager(usage="Run synchronizations.")
sync.add_command('showtimes', SyncShowtimes())
sync.add_command('all', SyncAll())
