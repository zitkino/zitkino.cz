# -*- coding: utf-8 -*-


import os
from collections import OrderedDict

from flask import request, render_template, send_from_directory

from . import app, parsers, log
from .models import Showtime, Film, Cinema
from .image import render_image, Image, PlaceholderImage


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
    cinemas = set()

    # prepare data for listing of films
    data = OrderedDict()
    for showtime in Showtime.upcoming():
        day = showtime.starts_at_day
        data.setdefault(day, {}).setdefault(showtime.film, []).append(showtime)

    days = data.keys() if more else data.keys()[:less_items]
    for day, films in data.items():
        if day in days:
            films = OrderedDict(sorted(
                films.items(),
                key=lambda (f, s): f.rating, reverse=True
            ))
            for film, showtimes in films.items():
                films[film] = sorted(showtimes, key=lambda s: s.starts_at)
                cinemas.update(s.cinema for s in showtimes)
            data[day] = films
        else:
            del data[day]

    # cinemas
    cinemas = sorted(
        (c for c in cinemas if not c.is_multiplex),
        key=lambda c: (c.priority, c.name)
    )

    # stats
    today_any_showtimes = bool(Showtime.today().count())

    # render the template
    return render_template('index.html', data=data, more=more,
                           cinemas=cinemas, less_items=less_items,
                           today_any_showtimes=today_any_showtimes)


@app.route('/film/<film_slug>')
def film(film_slug):
    film = Film.objects.get_or_404(slug=film_slug)
    return render_template('film.html', film=film)


@app.route('/cinema/<cinema_slug>-brno')
def cinema(cinema_slug):
    cinema = Cinema.objects.get_or_404(slug=cinema_slug)
    return render_template('cinema.html', cinema=cinema)


@app.route('/favicon.ico')
@app.route('/apple-touch-icon.png')
@app.route('/robots.txt')
@app.route('/humans.txt')
def static_files():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, request.path.lstrip('/'))


@app.route('/images/poster/<film_slug>.jpg')
def poster(film_slug):
    try:
        resize = parsers.resize(request.args.get('resize', 'x'))
        crop = request.args.get('crop')

        film = Film.objects.get_or_404(slug=film_slug)
        if film.url_poster:
            img = Image.from_url(film.url_poster)
            return render_image(img, resize=resize, crop=crop)
    except Exception:
        log.exception()

    img = PlaceholderImage('#EEE', size=resize)
    return render_image(img, crop=crop)


@app.route('/images/cinema-photo/<cinema_slug>.jpg')
def cinema_photo(cinema_slug):
    try:
        resize = parsers.resize(request.args.get('resize', 'x'))
        crop = request.args.get('crop')

        cinema = Cinema.objects.get_or_404(slug=cinema_slug)
        filename = os.path.join(
            app.root_path, 'static/images', cinema.slug + '.jpg'
        )

        if os.path.exists(filename):
            with open(filename) as f:
                img = Image(f)
                return render_image(img, resize=resize, crop=crop)
    except Exception:
        log.exception()

    img = PlaceholderImage('#EEE', size=resize)
    return render_image(img, crop=crop)
