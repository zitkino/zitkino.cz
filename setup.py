#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


package_init = 'zitkino/__init__.py'
with open(package_init, 'r') as f:
    match = re.search(r'__version__ = \'([^\'"]*)\'', f.read())
    if match:
        version = match.group(1)
    else:
        raise RuntimeError('Missing version number.')


requirements = [
    'flask',
    'gunicorn',
    'gevent',
    'beautifulsoup4',
    'requests',
    'python-dateutil',
    'flask-mongoengine',
]


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
    entry_points={
        'console_scripts': [
            'zitkino = zitkino.tasks:main',
        ],
    }
)
