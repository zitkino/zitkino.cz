# -*- coding: utf-8 -*-
"""Base MongoDB models (heavily inspired by Flask-MongoEngine)"""


import itertools
from collections import Mapping, OrderedDict

import mongoengine
from flask import abort
from mongoengine import ValidationError
from mongoengine.base.fields import BaseField
from mongoengine.queryset import MultipleObjectsReturned, DoesNotExist


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
        self.TagsField = TagsField

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

        # lazy connection
        mongoengine.register_connection(
            mongoengine.DEFAULT_CONNECTION_NAME,
            conn_settings.pop('db', None),
            **conn_settings
        )


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


### Custom model base class

class Document(mongoengine.Document):

    meta = {'abstract': True,
            'queryset_class': QuerySet}


### Custom fields

class TagsField(BaseField):
    """Dealing with the fact that MongoDB's dict keys may not
    contain "." or "$" characters - storing tags serialized as a list.
    """

    def validate(self, value):
        if not isinstance(value, dict):
            self.error('Only dictionaries may be used in a tag field')

    def to_mongo(self, value):
        return list(itertools.chain(*value.items()))

    def to_python(self, value):
        tags = OrderedDict()

        if isinstance(value, list):
            value = zip(* (2 * [iter(value)]))
        elif isinstance(value, Mapping):
            value = value.items()
        else:
            raise TypeError

        for k, v in sorted(value, key=lambda (k, v): k):
            tags[k] = v
        return tags
