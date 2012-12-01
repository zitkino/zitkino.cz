# -*- coding: utf-8 -*-


import re
import time
import datetime
from fabric.api import *


version_files = (
    {
        'name': 'zitkino/__init__.py',
        're': re.compile(r"__version__ = '([^']+)'"),
    },
    {
        'name': 'zitkino/config.py',
        're': re.compile(r"USER_AGENT = 'zitkino/([^ ]+)"),
    },
)


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
    version = '0.0.dev'
    new_suffix = '.dev' + str(int(time.time()))
    replace_re = re.compile(r'\([^\)]+\)')

    for file in version_files:
        with open(file['name'], 'r') as f:
            code = f.read()

        match = file['re'].search(code)
        if match:
            version = match.group(1)

        if '.dev' in version:
            version = re.sub(r'\.dev\d*', new_suffix, version)
        else:
            version += new_suffix

        puts('Bumping version in {file} to {ver}.'.format(
            file=file['name'], ver=version))
        version_code = replace_re.sub(version, file['re'].pattern)
        code = file['re'].sub(version_code, code)

        with open(file['name'], 'w') as f:
            f.write(code)

    return version


def test():
    """Run testsuite."""
    local('python setup.py test')


def deploy():
    """Deploy application to Heroku."""
    execute(test)

    now = datetime.datetime.now()
    user = local('git config --get user.name', capture=True)

    app = _heroku_app()
    branch = _git_branch()
    heroku_remotes = [r for r in _git_remotes()
                      if r.startswith('heroku')]

    version = bump_dev_version()
    for f in version_files:
        local('git add ' + f['name'])
    local('git commit -m "Version bump."')

    for remote in heroku_remotes:
        local('git push {remote} {branch}:master'.format(
            branch=branch, remote=remote))
    local('heroku run zitkino sync-static --app ' + app)

    tag = 'release-' + version
    msg = now.strftime('Release by {name} on %a, %d %b, %H:%M.'.format(
        name=user))
    local('git tag -a "{tag}" -m "{msg}"'.format(tag=tag, msg=msg))
    local('git push --tags origin {branch}:{branch}'.format(
        branch=branch))


def cron():
    """Immediately launch the cron job."""
    local('heroku run worker --app {app}'.format(
        app=_heroku_app()))
