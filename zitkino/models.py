# -*- coding: utf-8 -*-


from __future__ import division

from zitkino import db


class Cinema(db.Document):

    name = db.StringField(required=True)
    url = db.StringField()
    slug = db.StringField(required=True, unique=True)

    street = db.StringField()
    town = db.StringField()
    coords = db.GeoPointField()


class Showtime(db.EmbeddedDocument):

    cinema = db.ReferenceField(Cinema, dbref=False)
    starts_at = db.DateTimeField()

    meta = {
        'ordering': ['-starts_at']
    }


class Film(db.Document):

    id_csfd = db.IntField()
    id_imdb = db.IntField()
    id_synopsitv = db.IntField()

    title = db.StringField(required=True)
    slug = db.StringField(required=True, unique=True)
    year = db.IntField()
    length = db.IntField()

    rating_csfd = db.FloatField()
    rating_imdb = db.FloatField()
    rating_fffilm = db.FloatField()

    url_csfd = db.StringField()
    url_imdb = db.StringField()
    url_fffilm = db.StringField()
    url_synopsitv = db.StringField()

    showtimes = db.ListField(db.EmbeddedDocumentField(Showtime))

    @property
    def length_hours(self):
        return round(self.length / 60, 1)

    @property
    def rating(self):
        ratings = []
        if self.rating_csfd:
            ratings.append(self.rating_csfd)
        if self.rating_imdb:
            ratings.append(self.rating_imdb)
        if self.rating_fffilm:
            ratings.append(self.rating_fffilm)
        return round(sum(ratings) / len(ratings), 0)


data = [
    Cinema(
        name=u'Letní kino Na Dobráku',
        url='http://kinonadobraku.cz',
        slug='brno-letni-kino-na-dobraku',
        street=u'Dobrovského 29',
        town=u'Brno',
        coords=(49.2181389, 16.5888692)
    ),
    Cinema(
        name=u'Starobrno letní kino',
        url='http://www.letnikinobrno.cz',
        slug='brno-starobrno-letni-kino',
        street=u'Lidická 12',
        town=u'Brno',
        coords=(49.2013969, 16.6077600)
    ),
    Cinema(
        name=u'Kino Lucerna',
        url='http://www.kinolucerna.info',
        slug='brno-kino-lucerna',
        street=u'Minská 19',
        town=u'Brno',
        coords=(49.2104939, 16.5855358)
    ),
    Cinema(
        name=u'Kino Art',
        url='http://www.kinoartbrno.cz',
        slug='brno-kino-art',
        street=u'Cihlářská 19',
        town=u'Brno',
        coords=(49.2043861, 16.6034708)
    ),
]
