# -*- coding: utf-8 -*-

import flask
from flask import Flask

from flask_api_connector import ApiConnector, Paths


class Index:
    def get(self):
        return {
            'type': 'index',
            'message': 'example',
        }


class About:
    def get(self):
        return {
            'type': 'about',
            'message': 'this is an example api.',
        }


if __name__ == '__main__':
    app = Flask(__name__)

    paths = Paths([
        ('', Index),
        ('/about', About),
    ])

    ApiConnector(paths=paths, base_url='/api').init_app(app)

    app.run()
