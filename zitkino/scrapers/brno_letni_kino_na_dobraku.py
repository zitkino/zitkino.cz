# -*- coding: utf-8 -*-


from . import cinemas, scrapers


cinemas.register(
    name=u'Letní kino Na Dobráku',
    url='http://kinonadobraku.cz',
    street=u'Dobrovského 29',
    town=u'Brno',
    coords=(49.2181389, 16.5888692)
)


@scrapers.register
def scrape():
    return ()

# https://github.com/honzajavorek/zitkino.cz/blob/standalone-app/zitkino/scrapers/cinemas.py#L46
