#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import logging

from .sync import sync
from .models import data
from . import __version__


### Utilities ###


tasks = []
__all__ = ['main']


def task(func):
    """Decorate function to register it as a task."""
    func_name = func.__name__
    command = func_name.replace('_', '-')

    tasks.append((command, func))
    __all__.append(func_name)  # only main and tasks should be imported

    return func


def help():
    """Print help."""
    longest_name = max(dict(tasks).keys(), key=len)

    help = ''
    for name, func in tasks:
        adjusted_name = name.ljust(len(longest_name) + 1)
        command_help = "\t{name}\t{func.__doc__}\n".format(
            name=adjusted_name,
            func=func)
        help += command_help

    print >> sys.stderr, "usage: zitkino task\ntasks:\n" + help


def main(args=None):
    """Simple main controller."""
    args = args or sys.argv[1:]
    try:
        if len(args) > 1:  # no other extra arguments supported
            raise LookupError("Too much arguments.")
        task_name = args[0]
        task = dict(tasks)[task_name]  # task lookup

    except LookupError:
        help()  # in case of any failure, print usage
        sys.exit(1)

    sys.exit(task())  # call the task and exit


### Tasks ###


@task
def version():
    """Print version."""
    print __version__


@task
def sync_static():
    """Sync static data."""
    for document in data:
        logging.info("Sync of '%s' / '%s' object.",
                     document.__class__.__name__,
                     document.slug)

        found = document.__class__.objects(slug=document.slug).first()
        if found:
            logging.info("Object found in db.")
            document.id = found.id
            document.save()  # update
            logging.info("Object updated.")
        else:
            document.save()  # insert
            logging.info("Object inserted.")


task(sync)


### Invocation directly from CLI ###


if __name__ == '__main__':
    # Usually the main function is called directly, not
    # from this place. Look for entry_points/console_scripts
    # in setup.py to understand.
    main()
