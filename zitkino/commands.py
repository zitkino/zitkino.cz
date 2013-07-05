# -*- coding: utf-8 -*-


import logging

from flask.ext.script import Manager, Command

from .models import Cinema
from . import __version__ as version
from .scrapers import scrapers, cinemas


class Version(Command):
    """Print version."""

    def run(self):
        print version


class SyncCinemas(Command):
    """Sync cinemas."""

    def _sync_cinema(self, cinema):
        found = Cinema.objects.with_slug(cinema.slug).first()
        if found:
            cinema.id = found.id
            action = "Update"
        else:
            action = "Insert"
        logging.info(u"%s: %s", action, cinema.slug)
        cinema.save()

    def run(self):
        for cinema in cinemas:
            self._sync_cinema(cinema)


class SyncShowtimes(Command):
    """Sync showtimes."""

    def _sync_showtime(self, showtime):
        logging.info(
            u"Showtime: %s | %s | %s",
            showtime.starts_at,
            showtime.cinema.name,
            showtime.film.title_main,
        )
        showtime.save()

    def run(self):
        for scraper in scrapers:
            logging.info(u"Scraper: %s", scraper.__module__)
            results = scraper()
            if results:
                for showtime in results:
                    self._sync_showtime(showtime)


sync = Manager(usage="Run synchronizations.")
sync.add_command('cinemas', SyncCinemas())
sync.add_command('showtimes', SyncShowtimes())
