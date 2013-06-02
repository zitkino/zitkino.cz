web: uwsgi --http 0.0.0.0:$PORT -w zitkino:app --gevent 1024 -l 100 -p 1 -L
cron: zitkino sync
