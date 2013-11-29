# -*- coding: utf-8 -*-


import times
from flask.ext.script import Manager, Command

from . import log
from .scrapers import scrapers
from . import __version__ as version
from .models import Cinema, Showtime, Film


class Version(Command):
    """Print version."""

    def run(self):
        print version


class SyncShowtimes(Command):
    """Sync showtimes."""

    def _sync_showtime(self, showtime):
        if showtime.starts_at >= times.now():
            log.showtime(showtime)
            showtime.save()

    def _sync_cinema(self, cinema, showtimes):
        log.scraper_info(cinema.name)

        sync_start = times.now()
        counter = 0

        try:
            for showtime in showtimes:
                self._sync_showtime(showtime)
                counter += 1
        except:
            log.exception()
        else:
            query = Showtime.objects(cinema=cinema, scraped_at__lt=sync_start)
            query.delete()
        finally:
            log.scraper_info('created %d showtimes', counter)

    def run(self):
        for cinema_slug, scraper in scrapers.items():
            cinema = Cinema.objects(slug=cinema_slug).get()
            showtimes = scraper()
            if showtimes:
                self._sync_cinema(cinema, showtimes)


class SyncPairing(Command):
    """Find unpaired showtimes and try to find films for them."""

    def run(self):
        pass


class SyncCleanup(Command):
    """Find redundant films and showtimes and delete them to keep
    the db lightweight.
    """

    def run(self):
        now = times.now()

        # delete redundant showtimes
        Showtime.objects.filter(starts_at__lt=now).delete()

        # delete redundant films
        for film in Film.objects.all():
            if not Showtime.objects.filter(film_paired=film).count():
                film.delete()


class SyncUpdate(Command):
    """Find paired films and try to get newer/more complete data for them."""

    def run(self):
        pass


class SyncAll(Command):
    """Sync all."""

    def run(self):
        SyncShowtimes().run()
        SyncPairing().run()
        SyncCleanup().run()
        SyncUpdate().run()


sync = Manager(usage="Run synchronizations.")
sync.add_command('showtimes', SyncShowtimes())
sync.add_command('all', SyncAll())
