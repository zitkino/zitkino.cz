# -*- coding: utf-8 -*-


import logging

from .scrapers import scrapers
from .utils import deflate_exceptions


def sync():
    """Sync dynamic data (showtimes)."""
    for scraper in scrapers:
        logging.info("Scraping: %s", scraper.__module__.split('.')[-1])
        scraper = deflate_exceptions(scraper)
        for showtime in scraper():
            logging.info("Saving showtime: %r", showtime)
            showtime.save()
