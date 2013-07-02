# -*- coding: utf-8 -*-


from flask.ext.script import Command

from .sync import sync, sync_static
from . import __version__ as version


class Version(Command):
    """Print version."""

    def run(self):
        print version


class SyncStatic(Command):
    """Sync static data (cinemas)."""

    def run(self):
        sync_static()


class Sync(Command):
    """Sync dynamic data (showtimes)."""

    def run(self):
        sync()
