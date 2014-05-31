#!/usr/bin/env python
# -*- coding: utf-8 -*-


from zitkino import app
from zitkino.log import log_exceptions
from zitkino.commands import sync, Purge

from flask.ext.assets import ManageAssets
from flask.ext.script import Manager as BaseManager, Server


class Manager(BaseManager):

    @log_exceptions
    def run(self, *args, **kwargs):
        return super(Manager, self).run(*args, **kwargs)


manager = Manager(app)

manager.add_command('runserver', Server(host='0.0.0.0'))
manager.add_command('assets', ManageAssets())
manager.add_command('sync', sync)
manager.add_command('purge', Purge())


if __name__ == '__main__':
    manager.run()
