#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
#from clize import clize, run

import zitkino


#@clize
def sync():
    print 'sync'


#@clize
def version():
    print zitkino.__version__


def main():
    #run((sync, version))
    if sys.argv[1] == 'sync':
        sync()
    elif sys.argv[1] == 'version':
        version()


if __name__ == '__main__':
    main()
