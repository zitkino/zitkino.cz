# -*- coding: utf-8 -*-


import re
from fabric.api import *


def _parse_git_remotes():
    git_cmd = "git remote 2> /dev/null"
    return local(git_cmd, capture=True).split()


def _parse_git_branch():
    git_cmd = "git branch --no-color 2> /dev/null"
    branches = local(git_cmd, capture=True)

    # parse active branch
    match = re.search(r'\* ([\w\-_]*)', branches)
    if match:
        return match.group(1)
    return None


def _parse_procfile():
    proc = {}
    with open('Procfile') as f:
        lines = f.readlines()
    for line in filter(None, lines):
        name, cmd = line.split(': ', 2)
        proc[name] = cmd.strip()
    return proc


def deploy():
    """Deploy application to Heroku."""
    branch = _parse_git_branch()
    heroku_remotes = [r for r in _parse_git_remotes()
                      if r.startswith('heroku')]
    for remote in heroku_remotes:
        local('git push {remote} {branch}:master'.format(
            branch=branch, remote=remote))


def cron():
    """Immediately launch the cron job."""
    proc = _parse_procfile()
    local('heroku run "{proc[worker]}"'.format(proc=proc))
