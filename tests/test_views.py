# -*- coding: utf-8 -*-

from unittest.mock import patch

from flask import Response, g, json, request, session

from flask_api_connector.views import BaseView


def test_basic_view_has_methods(app):
    class Index:
        def get(self):
            pass

        def put(self):
            pass

    class TargetView(BaseView, Index):
        pass

    assert hasattr(TargetView, 'get')
    assert hasattr(TargetView, 'put')


def test_pass_request_to_method(app):
    class Index:
        def get(self, request):
            return request

    with app.app_context():
        class TargetView(BaseView, Index):
            pass

        with patch('flask_api_connector.views.jsonify') as jsonify:
            jsonify.side_effect = lambda x: x
            view = TargetView.as_view('test')
            view_cls = view.view_cls()

            assert view_cls.get() is request


def test_pass_session_to_method(app):
    class Index:
        def put(self, session):
            return session

    with app.app_context():
        class TargetView(BaseView, Index):
            pass

        with patch('flask_api_connector.views.jsonify') as jsonify:
            jsonify.side_effect = lambda x: x
            view = TargetView.as_view('test')
            view_cls = view.view_cls()

            assert view_cls.put() is session


def test_pass_g_to_method(app):
    class Index:
        def post(self, g):
            return g

    with app.app_context():
        class TargetView(BaseView, Index):
            pass

        with patch('flask_api_connector.views.jsonify') as jsonify:
            jsonify.side_effect = lambda x: x
            view = TargetView.as_view('test')
            view_cls = view.view_cls()

            assert view_cls.post() is g


def test_pass_multiple_args_to_method(app):
    class Index:
        def get(self, request, session, g):
            return {
                'request': request,
                'session': session,
                'g': g
            }

    with app.app_context():
        class TargetView(BaseView, Index):
            pass

        with patch('flask_api_connector.views.jsonify') as jsonify:
            jsonify.side_effect = lambda x: x
            view = TargetView.as_view('test')
            view_cls = view.view_cls()

            kw = view_cls.get()

            assert kw['request'] is request
            assert kw['session'] is session
            assert kw['g'] is g


def test_dispatch_methods(app, client):
    class Index:
        pass

    methods = ['GET', 'POST', 'PUT', 'DELETE']

    for meth in methods:
        def method(self):
            return {'method': meth}

        setattr(Index, meth.lower(), method)

    class TargetView(BaseView, Index):
        pass

    app.add_url_rule('/', view_func=TargetView.as_view('index'))

    for meth in methods:
        # each request should return method name
        # and method name is stored in the header
        resp = getattr(client, meth.lower())('/')
        data = json.loads(resp.data)
        assert data.get('method') == meth


def test_return_405_if_request_non_registered_method(app, client):
    class Index:
        def get(self):
            return 'GET'

    class TargetView(BaseView, Index):
        pass

    app.add_url_rule('/', view_func=TargetView.as_view('index'))

    resp = client.post('/')
    assert resp.status_code == 405


def test_dispatch_get_method_when_no_head_method(app, client):
    class Index:
        def get(self):
            return {'method': request.method}

    class TargetView(BaseView, Index):
        pass

    app.add_url_rule('/', view_func=TargetView.as_view('index'))
    resp = client.get('/')
    data = json.loads(resp.data)
    assert data.get('method') == 'GET'

    resp = client.head('/')
    assert resp.data == b''


def test_dispatch_head_method(app, client):
    class Index:
        def get(self):
            return {'method': request.method}

        def head(self):
            return Response('', headers={'X-Method': 'HEAD'})

    class TargetView(BaseView, Index):
        pass

    app.add_url_rule('/', view_func=TargetView.as_view('index'))
    resp = client.get('/')
    data = json.loads(resp.data)
    assert data.get('method') == 'GET'

    resp = client.head('/')
    assert resp.data == b''


def test_handle_dynamic_path(app, client):
    class Index:
        def get(self, name):
            return {'name': name}

    class TargetView(BaseView, Index):
        pass

    app.add_url_rule('/<string:name>', view_func=TargetView.as_view('index'))
    resp = client.get('/test')
    data = json.loads(resp.data)
    assert data.get('name') == 'test'
