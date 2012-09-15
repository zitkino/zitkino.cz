# -*- coding: utf-8 -*-


import times
from flask import render_template
from datetime import datetime, time

from zitkino import app


@app.route('/zitkino.<any(json, ics):ext>')
@app.route('/', defaults={'ext': 'html'})
def index(ext):
    now = times.now()
    today = datetime.combine(now.date(), time(0, 0))

    tpl_name = 'index.' + ext
    return render_template(tpl_name, films=[], now=now, today=today)
