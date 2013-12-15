# -*- coding: utf-8 -*-


import re

from zitkino.models import Film

from . import BaseFilmID, BaseFilmService


class DatabaseFilmID(BaseFilmID):
    url_re = re.compile(r'(.+)')


class DatabaseFilmService(BaseFilmService):

    name = u'Database'
    url_attr = 'id'  # film's ID

    def search(self, titles, year=None):
        params = {'titles_search__in': [title.lower() for title in titles]}
        if year is not None:
            params['year'] = year

        for film_match in Film.objects.filter(is_ghost=False, **params):
            for title_match in film_match.titles_search:
                if self._match_names(title.lower(), title_match):
                    return film_match
        return None

    def lookup(self, film_id):
        try:
            return Film.objects.get(id=film_id)
        except Film.DoesNotExist:
            return None
