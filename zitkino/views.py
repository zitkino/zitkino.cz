# -*- coding: utf-8 -*-


import os
from collections import OrderedDict

try:
    from cStringIO import cStringIO as StringIO
except ImportError:
    from StringIO import StringIO  # NOQA

from flask import (request, render_template, send_from_directory, send_file,
                   abort)

from . import app, log, parsers
from .models import Showtime, Film, Cinema


@app.context_processor
def inject_config():
    return {
        'ga_code': app.config['GA_CODE'],
        'debug': app.debug,
    }


@app.route('/')
def index():
    films = []
    cinemas = set()

    showtimes_by_film = {}
    for showtime in Showtime.upcoming.filter(film__ne=None):
        showtimes_by_film.setdefault(showtime.film, []).append(showtime)
        cinemas.add(showtime.cinema)

    films = OrderedDict(sorted(
        showtimes_by_film.items(),
        key=lambda (f, s): f.rating, reverse=True
    ))
    cinemas = sorted(cinemas, key=lambda c: (c.priority, c.name))

    return render_template('index.html', films=films, cinemas=cinemas)


@app.route('/film/<film_slug>')
def film(film_slug):
    film = Film.objects.get_or_404(slug=film_slug)

    # prepare data for listing of films
    data = OrderedDict()
    for showtime in film.showtimes_upcoming.all():
        day = showtime.starts_at_day
        data.setdefault(day, []).append(showtime)

    for day, showtimes in data.items():
        data[day] = sorted(showtimes, key=lambda s: s.starts_at)

    return render_template('film.html', film=film, data=data)


@app.route('/cinema/<cinema_slug>-brno')
def cinema(cinema_slug):
    cinema = Cinema.objects.get_or_404(slug=cinema_slug)

    # prepare data for listing of films
    data = OrderedDict()
    for showtime in cinema.showtimes_upcoming.filter(film__ne=None):
        day = showtime.starts_at_day
        data.setdefault(day, []).append(showtime)

    for day, showtimes in data.items():
        data[day] = sorted(showtimes, key=lambda s: s.starts_at)

    return render_template('cinema.html', cinema=cinema, data=data)


@app.route('/favicon.ico')
@app.route('/apple-touch-icon.png')
@app.route('/robots.txt')
@app.route('/humans.txt')
def static_files():
    static_dir = os.path.join(app.root_path, 'static')
    return send_from_directory(static_dir, request.path.lstrip('/'))


@app.route('/images/poster/<size>/<film_slug>.jpg')
@app.route('/images/poster/<film_slug>.jpg', defaults={'size': 'x'})
def poster(size, film_slug):
    film = Film.objects.get_or_404(slug=film_slug)
    try:
        size = parsers.size(size)
        if not size:
            abort(404)

        poster_file = film.select_poster_file(size=size)
        if poster_file:
            resp = send_file(poster_file.file, mimetype='image/jpeg')
            # resp.set_etag(poster_file.etag)
            # resp.make_conditional(request)
            return resp

    except Exception:
        log.exception()

    path = os.path.join(app.root_path, 'static/placeholder.png')
    return send_file(path, mimetype='image/png', conditional=True)


@app.route('/images/cinema-photo/<size>/<cinema_slug>.jpg')
@app.route('/images/cinema-photo/<cinema_slug>.jpg', defaults={'size': 'x'})
def cinema_photo(size, cinema_slug):
    cinema = Cinema.objects.get_or_404(slug=cinema_slug)
    try:
        size = parsers.size(size)
        if not size:
            abort(404)

        filename = '{}-{}x{}.jpg'.format(cinema.slug, *size)
        path = os.path.join(app.root_path, 'static/images', filename)
        if os.path.exists(path):
            return send_file(path, mimetype='image/jpeg', conditional=True)

    except Exception:
        log.exception()

    path = os.path.join(app.root_path, 'static/placeholder.png')
    return send_file(path, mimetype='image/png', conditional=True)
