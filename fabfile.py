# -*- coding: utf-8 -*-


import re
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


def deploy():
    """Deploy application to Heroku."""
    branch = _git_branch()
    heroku_remotes = [r for r in _git_remotes()
                      if r.startswith('heroku')]
    for remote in heroku_remotes:
        local('git push {remote} {branch}:master'.format(
            branch=branch, remote=remote))


def cron():
    """Immediately launch the cron job."""
    local('heroku run worker --app {app}'.format(
        app=_heroku_app()))
