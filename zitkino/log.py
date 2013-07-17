# -*- coding: utf-8 -*-


import logging


__all__ = (
    'config',
    'debug', 'info', 'warning', 'error', 'critical', 'exception',
    'scraper', 'showtime',
)


config = logging.basicConfig

debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical
exception = logging.exception


def scraper(msg, *args, **kwargs):
    info('Scraper: ' + msg, *args, **kwargs)


def showtime(showtime):
    info(
        u'Showtime: %s | %s | %s',
        showtime.starts_at,
        showtime.cinema.name,
        showtime.film.title_main
    )
