#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

import zitkino


requirements = [
    'Flask',
    'gunicorn',
    'gevent',
    'beautifulsoup4',
    'requests',
    'python-dateutil',
    'flask-heroku',
    'flask-sqlalchemy',
]


setup(
    name='zitkino',
    version=zitkino.__version__,
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
