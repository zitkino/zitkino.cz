# -*- coding: utf-8 -*-


from . import cinemas, scrapers


cinemas.register(
    name=u'Kino Lucerna',
    url='http://www.kinolucerna.info',
    street=u'Minská 19',
    town=u'Brno',
    coords=(49.2104939, 16.5855358)
)


@scrapers.register
def scrape():
    return ()
