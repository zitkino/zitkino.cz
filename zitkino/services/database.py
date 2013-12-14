# -*- coding: utf-8 -*-


import re

from zitkino.models import Film

from . import BaseFilmID, BaseFilmService


class DatabaseFilmID(BaseFilmID):
    url_re = re.compile(r'(.+)')


class DatabaseFilmService(BaseFilmService):

    name = u'Database'
    url_attr = 'id'  # film's ID

    def search(self, titles, year=None, directors=None):
        filters = ['titles']
        params = {'titles': titles}

        if year is not None:
            params['year'] = year
            filters.append('year')
        if directors:
            params['directors__in'] = directors
            filters.append('directors__in')

        for field in reversed(filters):
            try:
                match = Film.objects.get(is_ghost=False, **params)
            except (Film.DoesNotExist, Film.MultipleObjectsReturned):
                del params[field]
                if not params:
                    return None
            else:
                return match
        return None

    def lookup(self, film_id):
        try:
            return Film.objects.get(id=film_id)
        except Film.DoesNotExist:
            return None
