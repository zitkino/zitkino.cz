# -*- coding: utf-8 -*-


from . import cinemas, scrapers


cinema = cinemas.register(
    name=u'Kino Art',
    url='http://www.kinoart.cz',
    street=u'Cihlářská 19',
    town=u'Brno',
    coords=(49.2043861, 16.6034708)
)


@scrapers.register
def scrape():
    return ()
