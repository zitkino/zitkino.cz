# -*- coding: utf-8 -*-


import re
import os
from time import time
from fabric.api import *  # NOQA


project_dir = os.path.dirname(__file__)
version_file = os.path.join(project_dir, 'zitkino/__init__.py')


__all__ = ('deploy', 'ps', 'logs')


### Helpers

def capture(command):
    hide_all = hide('warnings', 'running', 'stdout', 'stderr')
    with settings(hide_all, warn_only=True):
        return local(command, capture=True)


def read_version():
    with open(version_file) as f:
        code = f.read()
    try:
        return re.search(r"__version__ = '([^']+)'", code).group(1)
    except AttributeError:
        abort('Unable to detect current version.')


def read_branch():
    branches = capture('git branch --no-color 2> /dev/null')
    try:
        return re.search(r'\* ([\w\-_]*)', branches).group(1)
    except AttributeError:
        abort('Unable to detect git branch.')


### Tasks

def deploy():
    """Push site to GitHub and deploy it to Heroku."""
    version = read_version()
    branch = read_branch()

    # tag version
    assert version.endswith('.dev'), "Version number does not end with '.dev'."
    tag = 'v' + version + str(int(time()))
    local('git tag {0}'.format(tag))

    # push to GitHub
    local('git push --tags origin {0}:{0}'.format(branch))

    # ensure MongoDB
    if 'MONGOLAB_URI' not in capture('heroku config | grep MONGOLAB_URI'):
        local('heroku addons:add mongolab:starter')

    # generate static files to throwaway branch 'deploy'
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        local('git branch -D deploy')
    local('git branch deploy && git checkout deploy')

    local('git add --force ' + os.path.join(static_dir, 'packed.css'))
    local('git add --force ' + os.path.join(static_dir, 'packed.js'))

    # push to Heroku
    local('git push heroku deploy:master --force')
    if 'web.1: up' not in capture('heroku ps'):
        local('heroku ps:scale web=1')

    # cleanup
    local('git checkout {0} && git branch -D deploy'.format(branch))


def ps():
    """Show remote process list."""
    local('heroku ps')


def logs():
    """Show remote logs."""
    local('heroku logs')
