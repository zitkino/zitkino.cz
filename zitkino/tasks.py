#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
#from clize import clize, run
# see https://github.com/epsy/clize/issues/2

from zitkino import __version__


#@clize
def sync():
    print 'sync'
    # http://packages.python.org/Flask-MongoKit/#request-and-app-context


#@clize
def version():
    print __version__


def main():
    #run((sync, version))
    if sys.argv[1] == 'sync':
        sync()
    elif sys.argv[1] == 'version':
        version()


if __name__ == '__main__':
    main()
