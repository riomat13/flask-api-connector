# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from flask import Flask

from flask_api_connector.core import _Path
from flask_api_connector.views import BaseView

Flask.testing = True
Flask.secret_key = 'test key'


@pytest.fixture
def app():
    app = Flask('test', root_path=Path(__file__).parent)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def paths():
    paths = []
    for i in range(3):
        class View(BaseView):
            def get(self):
                pass

        View.__name__ = f'View{i}'

        paths.append(
            _Path(f'/test{i}', View, f'name{i}')
        )
    return paths
