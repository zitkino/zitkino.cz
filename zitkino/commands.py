# -*- coding: utf-8 -*-


import times
from flask.ext.script import Manager, Command

from . import app, log, cache
from .scrapers import scrapers
from .models import Cinema, Showtime, Film
from .services import pair, search, DatabaseFilmService


class SyncShowtimes(Command):
    """Sync showtimes."""

    def run(self):
        for cinema_slug, scraper in scrapers.items():
            cinema = Cinema.objects.get(slug=cinema_slug)
            log.info('Scraping: %s', cinema.name)

            now = times.now()
            counter = 0

            with log.pass_on_exception():
                for showtime in scraper():
                    if showtime.starts_at >= times.now():
                        log.info('Scraping: %s', showtime)
                        showtime.save_overwrite(exclude=['film'])
                    counter += 1

                if counter != 0:
                    query = Showtime.objects(cinema=cinema, scraped_at__lt=now)
                    query.delete()
                # else it's suspicious situation, better don't delete anything

            log.info('Scraping: synchronized %d showtimes', counter)


class SyncPairing(Command):
    """Find unpaired showtimes and try to find films for them."""

    def run(self):
        for showtime in Showtime.unpaired():
            with log.pass_on_exception():
                film = showtime.film_scraped

                match = pair(film)
                if match:
                    log.info(u'Pairing: %s ← %s', film, match)
                    match.sync(film)
                    match.save_overwrite()
                    showtime.film = match
                else:
                    log.info(u'Pairing: %s ← ?', film)
                    ghost = film.to_ghost()
                    ghost.save_overwrite()
                    showtime.film = ghost
                showtime.save()


class SyncCleanup(Command):
    """Find redundant films and showtimes and delete them to keep
    the db lightweight.
    """

    def run(self):
        # delete old showtimes
        query = Showtime.objects.filter(starts_at__lt=times.now())
        count = query.count()
        query.delete()
        log.info('Cleanup: deleted %d old showtimes.', count)

        # delete redundant showtimes
        count = 0
        for showtime in Showtime.objects.all():
            with log.pass_on_exception():
                duplicates = Showtime.objects.filter(
                    id__ne=showtime.id,
                    cinema=showtime.cinema,
                    starts_at=showtime.starts_at,
                    film_scraped__title_main=showtime.film_scraped.title_main
                )
                count += duplicates.count()
                duplicates.delete()
        log.info('Cleanup: deleted %d redundant showtimes.', count)

        # delete redundant films
        for film in Film.objects.all():
            with log.pass_on_exception():
                if not film.showtimes.count():
                    log.info('Cleanup: deleting redundant film %s.', film)
                    film.delete()


class SyncUpdate(Command):
    """Find paired films and try to get newer/more complete data for them."""

    def run(self):
        for film in Film.objects.filter(is_ghost=False):
            for match in search(film, exclude=[DatabaseFilmService]):
                with log.pass_on_exception():
                    log.info(u'Update: %s ← %s', film, match)
                    film.sync(match)
                    film.save()


class SyncAll(Command):
    """Sync all."""

    def run(self):
        try:
            SyncShowtimes().run()
            SyncPairing().run()
            SyncCleanup().run()
            SyncUpdate().run()
        finally:
            ClearCache().run()


sync = Manager(usage="Run synchronizations.")
sync.add_command('showtimes', SyncShowtimes())
sync.add_command('pairing', SyncPairing())
sync.add_command('cleanup', SyncCleanup())
sync.add_command('update', SyncUpdate())
sync.add_command('all', SyncAll())


class ClearCache(Command):
    """Cleares the cache."""

    def run(self):
        with app.app_context():
            cache.clear()
        log.info('Cache: cleared.')


class Purge(Command):
    """Maintenance command. Wipes out all showtimes and films."""

    def run(self):
        Showtime.objects.delete()
        log.info('Purge: deleted all showtimes.')
        Film.objects.delete()
        log.info('Purge: deleted all films.')
