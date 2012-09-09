#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
#from clize import clize, run
# see https://github.com/epsy/clize/issues/2

from zitkino import __version__
from zitkino.models import data


#@clize
def sync():
    print 'sync'


#@clize
def update_data():
    for document in data:
        found = document.__class__.objects(slug=document.slug).first()
        if found:
            # update
            document.id = found.id
            document.save()
        else:
            # insert
            document.save()


#@clize
def version():
    print __version__


def main():
    #run((sync, version))
    if sys.argv[1] == 'sync':
        sync()
    elif sys.argv[1] == 'update_data':
        update_data()
    elif sys.argv[1] == 'version':
        version()


if __name__ == '__main__':
    main()
