# -*- coding: utf-8 -*-


import re
import unidecode


def slugify(string, sep='_'):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', sep, string)


def repr_name(cls):
    return '.'.join((cls.__module__, cls.__name__))
