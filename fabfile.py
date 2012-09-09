# -*- coding: utf-8 -*-


import re
import time
import datetime
from fabric.api import *


def _git_remotes():
    git_cmd = "git remote 2> /dev/null"
    return local(git_cmd, capture=True).split()


def _heroku_app():
    git_cmd = "git remote -v 2> /dev/null | grep -e 'heroku\s' | head -1"
    remote = local(git_cmd, capture=True)

    # parse app name
    match = re.search(r'git@heroku.com:([^.]+).git', remote)
    if match:
        return match.group(1)
    return None


def _git_branch():
    git_cmd = "git branch --no-color 2> /dev/null"
    branches = local(git_cmd, capture=True)

    # parse active branch
    match = re.search(r'\* ([\w\-_]*)', branches)
    if match:
        return match.group(1)
    return None


def _processes():
    proc = {}
    with open('Procfile') as f:
        lines = f.readlines()
    for line in filter(None, lines):
        name, cmd = line.split(': ', 2)
        proc[name] = cmd.strip()
    return proc


def bump_dev_version():
    """Bump version development suffix."""
    filename = 'zitkino/__init__.py'

    version = '0.0.dev'
    with open(filename, 'r') as f:
        code = f.read()

    match = re.search(r'__version__ = \'([^\'"]*)\'', code)
    if match:
        version = match.group(1)
    new_suffix = '.dev' + str(int(time.time()))

    if '.dev' in version:
        version = re.sub(r'\.dev\d*', new_suffix, version)
    else:
        version += new_suffix

    puts('Bumping version to {ver}.'.format(ver=version))
    version_code = '__version__ = \'{}\''.format(version)
    code = re.sub(r'__version__ = .+', version_code, code)

    with open(filename, 'w') as f:
        f.write(code)
    return version


def deploy():
    """Deploy application to Heroku."""
    now = datetime.datetime.now()
    user = local('git config --get user.name', capture=True)

    branch = _git_branch()
    heroku_remotes = [r for r in _git_remotes()
                      if r.startswith('heroku')]

    version = bump_dev_version()
    local('git add zitkino/__init__.py')
    local('git commit -m "version bump"')

    for remote in heroku_remotes:
        local('git push {remote} {branch}:master'.format(
            branch=branch, remote=remote))

    tag = 'release-' + version
    msg = now.strftime('release by {name} on %a, %d %b, %H:%M'.format(
        name=user))
    local('git tag -a "{tag}" -m "{msg}"'.format(tag=tag, msg=msg))
    local('git push --tags origin {branch}:{branch}'.format(
        branch=branch))


def cron():
    """Immediately launch the cron job."""
    local('heroku run worker --app {app}'.format(
        app=_heroku_app()))
