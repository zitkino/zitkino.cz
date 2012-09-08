#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requirements = filter(None, f.readlines())


setup(
    name='zitkino',
    version='1.0.0',
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
            'zitkino = zitkino:main',
        ],
    }
)
