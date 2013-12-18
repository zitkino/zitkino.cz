# -*- coding: utf-8 -*-


from hashlib import sha1

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from flask import send_file, request
from PIL import Image as PILImage, ImageEnhance

from . import http


class BaseImage(object):

    @property
    def size(self):
        return self.image.size

    def resize(self, width, height):
        image = self.image
        old_w, old_h = image.size

        # resize
        keep_height = (
            (old_w < old_h and width > height)
            or
            (old_w > old_h and width < height)
        )
        if keep_height:
            size = (old_w * height / old_h, height)
        else:
            size = (width, old_h * width / old_w)
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

    def to_stream(self, image_format='JPEG', **kwargs):
        if image_format == 'JPEG' and not kwargs:
            kwargs['quality'] = 100
        img_io = StringIO()
        self.image.save(img_io, image_format.upper(), **kwargs)
        img_io.seek(0)
        return img_io


class Image(BaseImage):

    def __init__(self, f):
        image = PILImage.open(f)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        self.image = image

    @classmethod
    def from_url(cls, url):
        """Download an image and provide it as memory stream."""
        response = http.Session().get(url)
        return cls(StringIO(response.content))


class PlaceholderImage(BaseImage):

    def __init__(self, color='#000', size=None):
        image = PILImage.new('RGB', size or (1, 1), color)
        self.image = image


def render_image(img, image_format='jpeg', resize=None, crop=None,
                 **format_options):
    if crop:
        img.crop(int(crop))
    if resize:
        img.resize(*resize)
    if crop or resize:
        img.sharpen()

    bytes_ = img.to_stream(image_format.upper(), **format_options).read()
    mimetype = 'image/' + image_format.lower()

    response = send_file(StringIO(bytes_), mimetype=mimetype)
    response.set_etag(sha1(bytes_).hexdigest())
    response.make_conditional(request)
    return response
