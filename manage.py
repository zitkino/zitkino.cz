#!/usr/bin/env python
# -*- coding: utf-8 -*-


from zitkino import app
from zitkino.commands import Version, SyncStatic, Sync

from flask.ext.assets import ManageAssets
from flask.ext.script import Manager, Server


manager = Manager(app)

manager.add_command('runserver', Server(host='0.0.0.0'))
manager.add_command('assets', ManageAssets())
manager.add_command('version', Version())
manager.add_command('sync-static', SyncStatic())
manager.add_command('sync', Sync())


if __name__ == '__main__':
    manager.run()
