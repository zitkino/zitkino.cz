# -*- coding: utf-8 -*-


from . import FilmDataService


class IMDbService(FilmDataService):

    name = u'IMDb'
    url_attr = 'url_imdb'
