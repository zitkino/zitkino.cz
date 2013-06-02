# -*- coding: utf-8 -*-
"""Base MongoDB models (inspired by Flask-MongoEngine)"""


import mongoengine
from flask import abort
from mongoengine import ValidationError
from mongoengine.queryset import (MultipleObjectsReturned, DoesNotExist,
                                  QuerySet)


def _include_mongoengine(obj):
    for module in mongoengine, mongoengine.fields:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


class MongoEngine(object):

    def __init__(self, app=None):
        _include_mongoengine(self)
        self.Document = Document
        self.EmbeddedDocument = EmbeddedDocument

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


class BaseQuerySet(QuerySet):
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


class ReprMixin(object):

    def _repr_name(self):
        cls = self.__class__
        return '.'.join((cls.__module__, cls.__name__))

    def __repr__(self):
        return '<{0}>'.format(self._repr_name())


class Document(ReprMixin, mongoengine.Document):

    meta = {'abstract': True,
            'queryset_class': BaseQuerySet}


class EmbeddedDocument(ReprMixin, mongoengine.EmbeddedDocument):

    meta = {'abstract': True}
