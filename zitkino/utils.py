# -*- coding: utf-8 -*-


import re
import unidecode


def slugify(s):
    s = unidecode.unidecode(s).lower()
    return re.sub(r'\W+', '-', s).strip('-')


def repr_name(cls):
    return '.'.join((cls.__module__, cls.__name__))
