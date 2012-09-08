# -*- coding: utf-8 -*-


import os
from flask import Flask
from flask_heroku import Heroku


app = Flask(__name__)
heroku = Heroku(app)


@app.route('/')
def hello():
    return 'Hello!'


if __name__ == '__main__':
    # bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
