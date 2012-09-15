#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from zitkino import __version__
from zitkino.sync import StaticDataSynchronizer, ShowtimesSynchronizer


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
        command_help = '\t{name}\t{func.__doc__}\n'.format(
            name=adjusted_name,
            func=func)
        help += command_help

    print >> sys.stderr, 'usage: zitkino task\ntasks:\n' + help


def main(args=None):
    """Simple main controller."""
    args = args or sys.argv[1:]  # can accept arguments also from code
    try:
        if len(args) > 1:  # no extra arguments supported
            raise LookupError('Too much arguments.')
        task_name = args[0]
        task = dict(tasks)[task_name]  # task lookup
        task()  # calling the task

    except LookupError:
        help()  # in case of any failure, print usage


### Tasks ###


@task
def version():
    """Print version."""
    print __version__


@task
def sync_static():
    """Synchronize static data."""
    s = StaticDataSynchronizer()
    s.sync()


@task
def sync():
    """Synchronize showtimes."""
    s = ShowtimesSynchronizer()
    s.sync()


### Invocation directly from CLI ###


if __name__ == '__main__':
    # Usually the main function is called directly, not
    # from this place. Look for entry_points/console_scripts
    # in setup.py to understand.
    main()
