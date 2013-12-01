# -*- coding: utf-8 -*-


from . import FilmDataService


class FFFilmService(FilmDataService):

    name = u'FFFilm'
    url_attr = 'url_fffilm'

    def search(self, title, year=None):
        pass

    def lookup(self, url):
        pass

