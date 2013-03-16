# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


# determine version
code = open('zitkino/__init__.py', 'r').read(500)
version = re.search(r'__version__ = \'([^\']*)\'', code).group(1)


# requirements
lines = open('requirements.txt').read().splitlines()
install_requires = filter(None, [line.split('#')[0].strip() for line in lines])


# setup configuration
setup(
    name='zitkino',
    version=version,
    author='Honza Javorek',
    author_email='jan.javorek@gmail.com',
    url='http://zitkino.cz',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=[
        ('https://github.com/sitesupport/gevent/tarball/1.0rc2#'
         'egg=gevent-1.0dev'),
    ],
    tests_require=['nose>=1.2.1'],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'zitkino = zitkino.tasks:main',
        ],
    }
)
