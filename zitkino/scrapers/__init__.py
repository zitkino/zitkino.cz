# -*- coding: utf-8 -*-


from werkzeug import import_string


scrapers = [import_string(__name__ + '.' + name).scrape for name in (
    'brno_kino_art',
    'brno_kino_lucerna',
    'brno_letni_kino_na_dobraku',
    'brno_starobrno_letni_kino',
)]
