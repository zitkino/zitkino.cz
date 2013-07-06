# -*- coding: utf-8 -*-
"""Base MongoDB models (heavily inspired by Flask-MongoEngine)"""


import mongoengine
from flask import abort
from mongoengine import ValidationError
from mongoengine.queryset import (MultipleObjectsReturned, DoesNotExist)


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


### Custom model base class

class Document(mongoengine.Document):

    meta = {'abstract': True,
            'queryset_class': QuerySet}
