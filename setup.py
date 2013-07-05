# -*- coding: utf-8 -*-


import re
from setuptools import setup, find_packages


# determine version
code = open('zitkino/__init__.py', 'r').read()
version = re.search(r'__version__ = \'([^\']*)\'', code).group(1)


# requirements
install_requires = []
dependency_links = []

for line in open('requirements.txt').read().splitlines():
    dep = line.split(' #')[0].strip()
    if not dep:
        continue
    if dep.startswith('http'):
        dependency_links.append(dep)
        dep = dep.split('#egg=')[1].replace('-', '==')
    install_requires.append(dep)


# setup configuration
setup(
    name='zitkino',
    version=version,
    author='Honza Javorek',
    author_email='jan.javorek@gmail.com',
    url='http://zitkino.cz',
    py_modules=['manage'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
)
