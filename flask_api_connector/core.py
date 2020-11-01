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
from typing import List

from .views import BaseView


class _Path(object):
    def __init__(self, rule: str, view_cls: type, name: str):
        self.rule = rule
        self.view_cls = view_cls
        self.name = name


class Paths(object):
    """Path converter.

    This is used for ApiConnctor as an adapter.

    The argument must be an iterable of tuple or list.

    Args:
        paths: list of tuple (path, View class, endpoint(optional))
        base_url: str (default: None)
            if this is set, add the url to all given paths

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
    def __init__(self, paths: List[tuple], base_url: str = None):
        self.paths = iter(paths)
        self.base_url = base_url

    def __iter__(self):
        for path_ in self.paths:
            path = self._process(path_)

            if hasattr(path, '__iter__') and not isinstance(path, _Path):
                for p in path:
                    yield p
            else:
                yield path

    def _process(self, path_):
        if isinstance(path_, type(self)):
            def update_url(path):
                if self.base_url is not None:
                    path.rule = os.path.join(self.base_url,
                                             path.rule.lstrip('/'))
                return path
            return map(update_url, path_)

        url, view_cls, *args = path_

        class View(BaseView, view_cls):
            pass

        name = args[0] if args else view_cls.__name__.lower()

        if self.base_url is not None:
            # to concatenate urls, second one must not start with '/'
            url = os.path.join(self.base_url, url.lstrip('/'))

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
        >>> connector = ApiConnector(paths, root_url='/api')
        >>> connector.init_app(app)
        >>> app.run()
    """

    def __init__(self, paths: Paths, root_url='/api'):
        """Api connector.

        Args:
            paths: Paths
            root_url: str (default: '/api')
                root url of the views
        """
        self.paths = paths
        self.root_url = root_url or '/'

    def init_app(self, app) -> None:
        for path in self.paths:
            rule = os.path.normpath(self.root_url + '/' + path.rule)

            app.add_url_rule(rule, view_func=path.view_cls.as_view(path.name))
