# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Rio Matsuoka
# All rights reserved.
"""
flask_api_connector
===================

This module provides a connector to connect reusable app to Flask app
to register the view methods.
"""


import os
from typing import List, NamedTuple

from .views import BaseView


class _Path(NamedTuple):
    rule: str
    view_cls: object
    name: str


class Paths(object):
    """Path converter.

    This is used for ApiConnctor as an adapter.

    The argument must be an iterable of tuple or list.
    Example:
        Paths([
            ('/first', First, 'firstitem'),
            ('/second', Second),
        ])

        where the first argument in the inner-most tuple is url rule,

        the second one is the target view class which has method such as get(),

        the third one, which is optional, is endpoint used in flask app.
        If endpoint is not explicitly provided,
        the lower-cased class name is used,
        so that the endpoint in the second tuple will be 'second'.
    """
    def __init__(self, paths: List[tuple]):
        self.paths = iter(paths)

    def __iter__(self):
        for path_ in self.paths:
            path = self.process(path_)
            yield path

    def process(self, path):
        url, view_cls, *args = path

        class View(BaseView, view_cls):
            pass

        name = args[0] if args else view_cls.__name__.lower()

        path = _Path(rule=url,
                     view_cls=View,
                     name=name)
        return path


class ApiConnector(object):
    """Connect view class to flask app.
    These methods can have arguments as request, session and/or g.

    Example:
        >>> from flask import Flask
        >>> from flask_api_connector import ApiConnector, Paths
        >>>
        >>> class First:
        ...    def get(self, request):
        ...        # do something
        ...        return result
        ...
        >>> class Second:
        ...    def get(self):
        ...        return 'get'
        ...    def post(self):
        ...        return 'post'
        ...
        >>> app = Flask('example')
        >>>
        >>> paths = Paths([
        ...    ('/first', First, 'firstitem'),
        ...    ('/second', Second),
        ...])
        >>>
        >>> connector = ApiConnector(paths, base_url='/api')
        >>> connector.init_app(app)
        >>> app.run()
    """

    def __init__(self, paths: Paths, base_url='/api'):
        """Api connector.

        Args:
            paths: Paths
            base_url: str (default: '/api')
                base url of the views
        """
        self.paths = paths
        self.base_url = base_url

    def init_app(self, app) -> None:
        for path in self.paths:
            rule = os.path.normpath(self.base_url + '/' + path.rule)

            app.add_url_rule(rule, view_func=path.view_cls.as_view(path.name))
