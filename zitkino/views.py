# -*- coding: utf-8 -*-


from collections import OrderedDict
import os

from flask import request, render_template, send_from_directory, abort

from . import app
from .image import generated_image, Image
from .models import Showtime, Film


@app.context_processor
def inject_config():
    return {
        'ga_code': app.config['GA_CODE'],
        'debug': app.debug,
    }


@app.route('/')
def index():
    upcoming = Showtime.upcoming().order_by('title_main', 'starts_at')
    data = OrderedDict()
    seen = set()
    for showtime in upcoming:
        key = showtime.starts_at_day, showtime.cinema.slug, showtime.film
        if key in seen:
            continue
        seen.add(key)
        data.setdefault(showtime.starts_at_day, []).append(showtime)
    return render_template('index.html', data=data)


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
    if not film.url_poster:
        abort(404)

    w, h = request.args.get('resize', 'x').split('x')
    crop = request.args.get('crop')

    img = Image.from_url(film.url_poster)
    if crop:
        img.crop(int(crop))
    if w and h:
        img.resize_crop(int(w), int(h))
    img.sharpen()

    return img.to_stream()
