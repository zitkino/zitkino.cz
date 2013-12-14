# -*- coding: utf-8 -*-


import re
import os
from time import time
from fabric.api import *  # NOQA


project_dir = os.path.dirname(__file__)
static_dir = os.path.join(project_dir, 'zitkino/static')
version_file = os.path.join(project_dir, 'zitkino/__init__.py')


__all__ = ('deploy', 'ps', 'logs', 'sync')


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

    # ensure Sentry
    if 'SENTRY_DSN' not in capture('heroku config | grep SENTRY_DSN'):
        local('heroku addons:add sentry:developer')

    try:
        # prepare throwaway branch 'deploy'
        with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
            local('git branch -D deploy')
        local('git branch deploy')
        local('git checkout deploy')

        # build and commit static files
        with shell_env(PYTHONDONTWRITEBYTECODE='1'):
            local('python manage.py assets -q --parse-templates build')
        local('git add --force ' + os.path.join(static_dir, 'css/packed.css'))
        local('git add --force ' + os.path.join(static_dir, 'js/packed.js'))
        local('git commit -m "Static files."')

        # push to Heroku
        local('git push heroku deploy:master --force')
        if 'web.1: up' not in capture('heroku ps'):
            local('heroku ps:scale web=1')

    finally:
        local('git reset HEAD')
        local('git checkout {0}'.format(branch))
        local('git branch -D deploy')


def sync():
    """Manual synchronization."""
    local('heroku run python manage.py sync all')


def ps():
    """Show remote process list."""
    local('heroku ps')


def logs():
    """Show remote logs."""
    local('heroku logs')
