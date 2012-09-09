# -*- coding: utf-8 -*-


from zitkino import db


class Cinema(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(250))
    url = db.Column(db.String(250))
    slug = db.Column(db.String(250))

    street = db.Column(db.String(500))
    town = db.Column(db.String(250))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)


class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_csfd = db.Column(db.Integer)
    id_imdb = db.Column(db.Integer)
    id_synopsitv = db.Column(db.Integer)

    title = db.Column(db.String(500))
    title_en = db.Column(db.String(500))
    title_cs = db.Column(db.String(500))
    slug = db.Column(db.String(250))

    year = db.Column(db.Integer)
    length = db.Column(db.Integer)
    length_hours # auto/generated

    rating # auto/generated
    rating_csfd = db.Column(db.Float)
    rating_imdb = db.Column(db.Float)
    rating_fffilm = db.Column(db.Float)

    url_csfd = db.Column(db.String(250))
    url_imdb = db.Column(db.String(250))
    url_fffilm = db.Column(db.String(250))
    url_synopsitv = db.Column(db.String(250))


class Showtime(db.Model):
    film_id = db.Column(db.Integer)
    cinema_id = db.Column(db.Integer)
    starts_at = db.Column(db.DateTime)
    ends_at # auto/generated
    slug = db.Column(db.String(250))
