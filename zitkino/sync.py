# -*- coding: utf-8 -*-


import logging

from .scrapers import scrapers
from .models import static_data
from .utils import deflate_exceptions


def sync():
    """Sync dynamic data (showtimes)."""
    for scraper in scrapers:
        logging.info("Scraping: %s", scraper.__module__)
        scraper = deflate_exceptions(scraper)

        for showtime in scraper():
            logging.info("Showtime: %r", showtime)
            showtime.save()


def sync_static():
    """Sync static data (cinemas)."""
    for doc in static_data:
        found = doc.__class__.objects.with_slug(doc.slug)
        if found:
            doc.id = found.id
            action = "Update"
        else:
            action = "Insert"
        doc.save()
        logging.info("%s: %r", action, doc)
