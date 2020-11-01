# -*- coding: utf-8 -*-

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


class Hello:
    # can take variable
    def get(self, name):
        return f'Hello {name}!'


class Double:
    def get(self, number):
        return number * 2


if __name__ == '__main__':
    app = Flask(__name__)

    app_paths = Paths([
        ('/hello/<string:name>', Hello),
        ('/double/<int:number>', Double),
    ], base_url='/app')

    paths = Paths([
        ('', Index),
        ('/about', About),
        app_paths
    ])

    ApiConnector(paths=paths, root_url='/api').init_app(app)

    app.run()
