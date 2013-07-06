# -*- coding: utf-8 -*-


import logging

import times
from flask.ext.script import Manager, Command

from .scrapers import scrapers
from . import __version__ as version
from .models import Showtime, Cinema


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

    def run(self):
        for cinema_slug, scraper in scrapers.items():
            try:
                cinema = Cinema.objects(slug=cinema_slug).get()
                sync_start = times.now()

                logging.info(u"Scraper: %s", cinema_slug)
                showtimes = scraper() or []

                for showtime in showtimes:
                    self._sync_showtime(showtime)

            except Exception as e:
                logging.exception(e)
            else:
                logging.info('Scraper: Deleting obsolete showtimes.')
                Showtime.objects(cinema=cinema,
                                 scraped_at__lt=sync_start).delete()


class SyncAll(Command):
    """Sync all."""

    def run(self):
        SyncShowtimes().run()


sync = Manager(usage="Run synchronizations.")
sync.add_command('showtimes', SyncShowtimes())
sync.add_command('all', SyncAll())
