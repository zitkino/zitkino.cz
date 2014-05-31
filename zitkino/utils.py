# -*- coding: utf-8 -*-


import re

from unidecode import unidecode
from PIL import Image, ImageEnhance


class cached_property(object):

    def __init__(self, factory, attr_name=None):
        self._attr_name = attr_name or factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        attr = self._factory(instance)
        setattr(instance, self._attr_name, attr)
        return attr


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


def create_thumbnail(image, size):
    if size == image.size:
        return image

    width, height = size
    old_w, old_h = image.size

    # resize
    keep_height = (
        (old_w < old_h and width > height)
        or
        (old_w >= old_h and width <= height)
    )
    if keep_height:
        size = (old_w * height / old_h, height)
    else:
        size = (width, old_h * width / old_w)
    image = image.resize(size, Image.ANTIALIAS)

    # crop the rest, centered
    left = abs(size[0] - width) / 2
    top = abs(size[1] - height) / 2

    box = (left, top, left + width, top + height)
    image = image.crop(box)

    # sharpen
    sharpener = ImageEnhance.Sharpness(image)
    return sharpener.enhance(1.6)
