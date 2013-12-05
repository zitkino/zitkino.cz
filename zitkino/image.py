# -*- coding: utf-8 -*-


from hashlib import sha1
from functools import wraps

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import requests
from flask import send_file, request
from PIL import Image as PILImage, ImageEnhance


class Image(object):

    def __init__(self, f):
        image = PILImage.open(f)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        self.image = image

    @property
    def size(self):
        return self.image.size

    def resize_crop(self, width, height):
        image = self.image
        is_rect = width == height
        old_w, old_h = image.size

        # resize by shorter side
        if width < height or (is_rect and old_w < old_h):
            size = (width, old_h * width / old_w)
        else:
            size = (old_w * height / old_h, height)
        image = image.resize(size, PILImage.ANTIALIAS)

        # crop the rest, centered
        left = abs(size[0] - width) / 2
        top = abs(size[1] - height) / 2

        box = (left, top, left + width, top + height)
        image = image.crop(box)

        self.image = image

    def crop(self, pixels):
        image = self.image

        w, h = image.size
        box = (pixels, pixels, w - pixels, h - pixels)
        image = image.crop(box)

        self.image = image

    def sharpen(self, sharpness=1.6):
        sharpener = ImageEnhance.Sharpness(self.image)
        self.image = sharpener.enhance(sharpness)

    def to_stream(self):
        img_io = StringIO()
        self.image.save(img_io, 'JPEG', quality=100)
        img_io.seek(0)
        return img_io

    @classmethod
    def from_url(cls, url):
        """Download an image and provide it as memory stream."""
        response = requests.get(url)
        response.raise_for_status()
        return cls(StringIO(response.content))


def generated_image(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        bytestring = f(*args, **kwargs).read()
        response = send_file(StringIO(bytestring), mimetype='image/jpeg')
        response.set_etag(sha1(bytestring).hexdigest())
        response.make_conditional(request)
        return response
    return wrapper
