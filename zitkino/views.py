# -*- coding: utf-8 -*-


import times
from flask import render_template
from datetime import datetime, time

from zitkino import app
from zitkino.models import Showtime


@app.route('/zitkino.<any(json, ics):ext>')
@app.route('/', defaults={'ext': 'html'})
def index(ext):
    now = times.now()
    today = datetime.combine(now.date(), time(0, 0))

    showtimes = Showtime.objects.find(
        starts_at__gte=now).order_by('-starts_at')

    tpl_name = 'index.' + ext
    return render_template(tpl_name, showtimes=showtimes, now=now, today=today)
