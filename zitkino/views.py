# -*- coding: utf-8 -*-


import os
from itertools import chain
from collections import OrderedDict

import times
from flask import request, render_template, send_from_directory

from . import app
from .models import Showtime, Film
from .image import generated_image, Image, PlaceholderImage


@app.context_processor
def inject_config():
    return {
        'ga_code': app.config['GA_CODE'],
        'debug': app.debug,
    }


@app.route('/more/', defaults={'more': True})
@app.route('/', defaults={'more': False})
def index(more):
    less_items = 2

    # prepare data for listing of films
    data = OrderedDict()
    for showtime in Showtime.upcoming():
        day = showtime.starts_at_day
        data.setdefault(day, {}).setdefault(showtime.film, []).append(showtime)

    days = data.keys() if more else data.keys()[:less_items]
    for day, films in data.items():
        if day in days:
            data[day] = [
                (
                    film, sorted(showtimes, key=lambda s: s.starts_at)
                )
                for (film, showtimes) in
                sorted(
                    films.items(),
                    key=lambda (f, s): f.rating, reverse=True
                )
            ]
        else:
            del data[day]

    # stats for the closest day
    closest_showtimes = list(
        chain(*[showtimes for (f, showtimes) in data.values()[0]])
    )
    cinemas_count = len(frozenset(s.cinema for s in closest_showtimes))
    showtimes_count = len(closest_showtimes)
    today_any_showtimes = bool(data.get(times.now().date(), False))

    # render the template
    return render_template('index.html', data=data, more=more,
                           less_items=less_items,
                           cinemas_count=cinemas_count,
                           showtimes_count=showtimes_count,
                           today_any_showtimes=today_any_showtimes)


@app.route('/film/<film_slug>')
def film(film_slug):
    raise NotImplementedError


@app.route('/cinema/<cinema_slug>')
def cinema(cinema_slug):
    raise NotImplementedError


@app.route('/favicon.ico')
@app.route('/apple-touch-icon.png')
@app.route('/robots.txt')
@app.route('/humans.txt')
def static_files():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, request.path.lstrip('/'))


@app.route('/images/poster/<film_id>.jpg')
@generated_image
def poster(film_id):
    film = Film.objects.get_or_404(id=film_id)

    w, h = request.args.get('resize', 'x').split('x')
    crop = request.args.get('crop')

    if not film.url_poster:
        if w and h:
            w, h = int(w), int(h)
        else:
            w, h = 1, 1
        return PlaceholderImage('#EEE', width=w, height=h).to_stream('PNG')

    img = Image.from_url(film.url_poster)
    if crop:
        img.crop(int(crop))
    if w and h:
        img.resize_crop(int(w), int(h))
    img.sharpen()

    return img.to_stream()
