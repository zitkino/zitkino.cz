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
        self.SaveOverwriteMixin = SaveOverwriteMixin
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


class SaveOverwriteMixin(object):

    meta = {'abstract': True}

    def _has_field(self, attr):
        """Checks existence of given model attribute. Attribute can
        be provided also in form of nested dot or double underscore notation.
        """
        try:
            self._get_field(attr)
        except AttributeError:
            return False
        return True

    def _get_field(self, attr):
        """Returns field object for given model attribute.
        Attribute can be provided also in form of nested dot or
        double underscore notation.
        """
        obj = self.__class__
        for part in attr.replace('__', '.').split('.'):
            obj = getattr(getattr(obj, 'document_type', obj), part)
        return obj

    def _get_value(self, attr):
        """Returns value of given model attribute. Attribute can be provided
        also in form of nested dot or double underscore notation.
        """
        obj = self
        for part in attr.replace('__', '.').split('.'):
            obj = getattr(obj, part)
        return obj

    @property
    def _unique_values(self):
        """Provides dictionary of unique attributes and their values. Nested
        unique attributes are returned in double underscore notation.
        """
        fields = {}
        for key in self._data.keys():
            if self._has_field(key):
                field = self._get_field(key)
                if field.unique:
                    fields[key] = self._get_value(key)
                for key in (field.unique_with or []):
                    fields[key.replace('.', '__')] = self._get_value(key)
            # else there were changes in model, continue
        return fields

    def save_overwrite(self, exclude=None, validate=True, clean=True):
        """Inserts or updates, depends on unique fields.

        :param exclude: Iterable of field names to be excluded from
                        inserting/updating (so they'll never be saved
                        and their existing values are never overwritten).
        """
        cls = self.__class__  # model class

        if validate:
            self.validate(clean=clean)

        # get all unique fields
        unique_values = self._unique_values
        if not len(unique_values):
            raise ValidationError('There are no unique constraints.')

        # prepare data to set
        exclude = frozenset(list(exclude or []) + ['id'])
        data = {}
        for key, value in self._data.items():
            if not self._has_field(key):
                continue
            if key in exclude:
                continue
            if value is not None:
                value = self._get_field(key).to_mongo(value)
            data['set__' + key] = value

        # select the object by its unique fields, perform upsert
        cls.objects.filter(**unique_values).update_one(upsert=True, **data)

        # set id (not very atomic...)
        self.id = cls.objects.get(**unique_values).id


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
