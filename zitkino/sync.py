# -*- coding: utf-8 -*-


import logging

from .scrapers import scrapers
from .models import static_data
from .utils import deflate_exceptions


def sync():
    """Sync dynamic data (showtimes)."""
    for scraper in scrapers:
        logging.info("Scraping: %s", scraper.__module__.split('.')[-1])
        scraper = deflate_exceptions(scraper)
        for showtime in scraper():
            logging.info("Saving showtime: %r", showtime)
            showtime.save()


def sync_static():
    """Sync static data (cinemas)."""
    for document in static_data:
        logging.info("Sync: %s %s",
                     document.__class__.__name__, document.slug)

        found = document.__class__.objects(slug=document.slug).first()
        if found:
            document.id = found.id
            document.save()  # update
            logging.info("Updated.")
        else:
            document.save()  # insert
            logging.info("Inserted.")
