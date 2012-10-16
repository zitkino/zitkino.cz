# -*- coding: utf-8 -*-


import times
from flask import render_template
from datetime import datetime, time, timedelta

from zitkino import app
from zitkino.models import Showtime, LogRecord


@app.route('/zitkino.<any(json):ext>')
@app.route('/', defaults={'ext': 'html'})
def index(ext):
    now = times.now()
    today = datetime.combine(now.date(), time(0, 0))

    showtimes = Showtime.objects(
        starts_at__gte=now).order_by('-starts_at')

    tpl_name = 'index.' + ext
    return render_template(tpl_name, showtimes=showtimes, now=now, today=today)


@app.route('/aktualizace')
def log():
    now = times.now()
    two_days_ago = datetime.combine(now - timedelta(2), time(0, 0))

    records = LogRecord.objects(
        action__exists=True,
        happened_at__gte=two_days_ago).order_by('-happened_at')

    return render_template('log.html', records=records)
