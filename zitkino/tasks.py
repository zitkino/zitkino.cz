#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
#from clize import clize, run
# see https://github.com/epsy/clize/issues/2

from zitkino import __version__
from zitkino.models import data


#@clize
def version():
    """Print version."""
    print __version__


#@clize
def sync():
    """Synchronize dynamic data (showtimes)."""
    print 'sync'
    # def scrape_films(self):
    #     films = []
    #     for driver in self.drivers:
    #         films += list(driver().scrape())
    #     sorted_films = sorted(films, key=lambda film: film.date)
    #     filtered_films = [f for f in sorted_films if f.date >= self.today]
    #     return filtered_films


#@clize
def update():
    """Insert or update static data defined in models."""
    for document in data:
        found = document.__class__.objects(slug=document.slug).first()
        if found:
            document.id = found.id
            document.save()
        else:
            document.save()


def main():
    #run((sync, version))
    try:
        task_name = sys.argv[1]
        task = globals()[task_name]
        task()
    except (IndexError, KeyError):
        print >> sys.stderr, 'Bad arguments.'
        sys.exit(1)


if __name__ == '__main__':
    main()
