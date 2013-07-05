# -*- coding: utf-8 -*-


import re

import unidecode


def slugify(string, sep='_'):
    string = unidecode.unidecode(string).lower()
    return re.sub(r'\W+', sep, string).strip(sep)
