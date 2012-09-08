# -*- coding: utf-8 -*-


from flask import Flask
from flask_heroku import Heroku


app = Flask(__name__)
heroku = Heroku(app)


@app.route('/')
def hello():
    return 'Hello!'


def main():
    pass
