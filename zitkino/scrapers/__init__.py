# -*- coding: utf-8 -*-


import pkgutil
import logging

from werkzeug import import_string


# automatically imports all submodules and cummulates their 'scrape' functions
# into 'scrapers' list
scrapers = []
for loader, module_name, is_package in pkgutil.walk_packages(__path__):
    module_name = __name__ + '.' + module_name
    scraper = getattr(import_string(module_name), 'scrape', None)
    if scraper:
        logging.debug("Scraper registered: %s", module_name)
        scrapers.append(scraper)
    else:
        logging.warning("Scraper couldn't be registered: %s", module_name)
