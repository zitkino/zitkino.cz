# -*- coding: utf-8 -*-


import re

from unidecode import unidecode


def slugify(string, sep='-'):
    string = unidecode(string).lower()
    string = re.sub(r'\W+', sep, string)
    return re.sub('{}+'.format(sep), sep, string).strip(sep)


def clean_whitespace(value):
    """Normalizes whitespace."""
    whitespace_re = re.compile(
        ur'[{0}\s\xa0]+'.format(
            re.escape(''.join(map(unichr, range(0, 32) + range(127, 160))))
        )
    )
    return whitespace_re.sub(' ', value).strip()
