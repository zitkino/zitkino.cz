# -*- coding: utf-8 -*-


from fabric.api import *


def debug():
    local('python pubfile.py')


def deploy():
    local('git push origin master')
    local('heroku run --app polar-brushlands-3976 python pub.py')
