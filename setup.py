#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


# Hack to prevent stupid "TypeError: 'NoneType' object is not callable"
# error in multiprocessing/util.py _exit_function when running `python
# setup.py test`
try:
    import multiprocessing
except ImportError:
    pass


# determine version
package_init = 'zitkino/__init__.py'
with open(package_init, 'r') as f:
    match = re.search(r'__version__ = \'([^\'"]*)\'', f.read())
    if match:
        version = match.group(1)
    else:
        raise RuntimeError('Missing version number.')


# required python packages
requirements = (
    'flask>=0.9',
    'gunicorn>=0.14.6',
    'gevent>=0.13.8',
    'beautifulsoup4>=4.1.3',
    'requests>=0.13.8',
    'times>=0.5',
    'python-dateutil>=2.1',
    'flask-mongoengine>=0.6',
    'fuzzywuzzy>=0.1',
    'unidecode>=0.04.9',
)


# setup configuration
setup(
    name='zitkino',
    version=version,
    author='Honza Javorek',
    author_email='jan.javorek@gmail.com',
    url='http://zitkino.cz',
    description='Best calendar of cinemas in Brno',
    license='ISC',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
    tests_require=['nose>=1.2.1'],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'zitkino = zitkino.tasks:main',
        ],
    }
)
