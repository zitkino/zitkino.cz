# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


# determine version
version = re.search(r'__version__ = \'([^\'"]*)\'',
                    open('zitkino/__init__.py').read()).group(1)


# setup configuration
setup(
    name='zitkino',
    version=version,
    author='Honza Javorek',
    author_email='jan.javorek@gmail.com',
    url='http://zitkino.cz',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=(
        'flask>=0.9',
        'gunicorn>=0.14.6',
        'gevent>=0.13.8',
        'requests>=0.13.8',
        'times>=0.5',
        'unidecode>=0.04.9',
        'flask-gzip==0.1',
    ),
    tests_require=['nose>=1.2.1'],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'zitkino = zitkino.tasks:main',
        ],
    }
)
