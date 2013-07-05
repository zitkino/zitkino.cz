# -*- coding: utf-8 -*-
"""Base MongoDB models (heavily inspired by Flask-MongoEngine)"""


import mongoengine
from flask import abort
from mongoengine import ValidationError
from mongoengine.queryset import (MultipleObjectsReturned, DoesNotExist)

from .utils import slugify


### Base MongoEngine adapter

def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


class MongoEngine(object):

    def __init__(self, app=None):
        _include_mongoengine(self)
        self.Document = Document
        self.SlugMixin = SlugMixin

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        conn_settings = {
            'db': app.config.get('MONGODB_DB', None),
            'username': app.config.get('MONGODB_USERNAME', None),
            'password': app.config.get('MONGODB_PASSWORD', None),
            'host': app.config.get('MONGODB_HOST', None),
            'port': int(app.config.get('MONGODB_PORT') or 0) or None
        }
        conn_settings = dict([(k, v) for k, v in conn_settings.items() if v])
        self.connection = mongoengine.connect(**conn_settings)


### Custom QuerySet

class QuerySet(mongoengine.queryset.QuerySet):
    """A base queryset with handy extras."""

    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except (MultipleObjectsReturned, DoesNotExist, ValidationError):
            abort(404)

    def first_or_404(self):
        obj = self.first()
        if obj is None:
            abort(404)
        return obj

    def with_slug(self, slug):
        return self.filter(_slug=slug)


### Model mixins

class SlugMixin(object):

    _slug = mongoengine.fields.StringField(required=True, unique=True,
                                           db_field='slug')

    def __init__(self, *args, **kwargs):
        super(SlugMixin, self).__init__(*args, **kwargs)
        if not self._slug:
            self._create_slug()

    @property
    def slug(self):
        self._create_slug()
        return self._slug

    def clean(self):
        try:
            self._create_slug()
        except ValueError as e:
            raise mongoengine.ValidationError(*e.args)
        super(SlugMixin, self).clean()

    def _create_slug(self):
        values = []
        for field_name in self._meta.get('slug', []):
            value = getattr(self, field_name)
            if value is None or not unicode(value):
                raise ValueError("Column {0} participates in slug, "
                                 "but it is empty.".format(field_name))
            values.append(unicode(value))
        self._slug = slugify('_'.join(values))


### Custom model base class

class Document(mongoengine.Document):

    meta = {'abstract': True,
            'queryset_class': QuerySet}
