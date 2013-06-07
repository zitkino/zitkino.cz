# -*- coding: utf-8 -*-


import re
import os
from fabric.api import *  # NOQA


project_dir = os.path.dirname(__file__)
version_file = 'zitkino/__init__.py'


if os.getcwd() != project_dir:
    abort('Not in project root. Please, cd to {0}.'.format(project_dir))


__all__ = ('deploy', 'ps', 'logs', 'css')


def capture(cmd):
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),
                  warn_only=True):
        return local(cmd, capture=True)


def bump_version():
    """Automatically bump version."""
    version_re = re.compile(r"__version__ = '([^']+)'")

    with open(version_file) as f:
        code = f.read()
    try:
        match = version_re.search(code)
        version = match.group(1)
    except AttributeError:
        abort('Unable to detect current version.')

    major, minor, micro = map(int, version.split('.'))
    micro += 1
    version = '.'.join(map(str, [major, minor, micro]))

    puts('Bumping version to {0}.'.format(version))
    code = version_re.sub("__version__ = '{0}'".format(version), code)

    with open(version_file, 'w') as f:
        f.write(code)
    return version


def deploy():
    """Push site to GitHub and deploy it to Heroku."""
    static_dir = os.path.join(project_dir, 'zitkino/static')

    # parse active branch
    branches = capture('git branch --no-color 2> /dev/null')
    match = re.search(r'\* ([\w\-_]*)', branches)
    if not match:
        abort('Unable to detect git branch.')
    branch = match.group(1)

    # check repository status
    if capture('git status -s'):
        abort('Modified files present in repository.')

    # if there is something to push & deploy, bump version
    if capture('git diff origin/$(git name-rev '
               '--name-only HEAD)..HEAD --name-status'):
        tag = 'v' + bump_version()
        local('git add ' + version_file)
        local('git commit --amend --no-edit')
        local('git tag {0}'.format(tag))

    # push to GitHub
    local('git push --tags origin {0}:{0}'.format(branch))

    # mongodb
    if 'MONGOLAB_URI' not in capture('heroku config | grep MONGOLAB_URI'):
        local('heroku addons:add mongolab:starter')

    # generate static files to throwaway branch 'deploy'
    with settings(hide('warnings', 'stdout', 'stderr'), warn_only=True):
        local('git branch -D deploy')
    local('git branch deploy && git checkout deploy')

    # push branch to Heroku
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
