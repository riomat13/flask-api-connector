# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Rio Matsuoka
# All rights reserved.
"""
flask_api_connector.views
=========================

View class to connect flask app

"""

import inspect
from functools import partialmethod, wraps

from flask import request, session, g, jsonify
from flask.views import http_method_funcs


def _make_jsonify(view_func):
    """Wrapper to convert dict to response object."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        out = view_func(*args, **kwargs)
        return jsonify(out)
    return wrapper


class BaseView(object):

    @classmethod
    def as_view(cls, name, *cls_args, **cls_kwargs):

        def view(*args, **kwargs):
            cls = view.view_cls(*cls_args, **cls_kwargs)
            return cls.dispatch_request(*args, **kwargs)

        methods = set()

        for meth in http_method_funcs:
            method = getattr(cls, meth, None)
            if method:
                methods.add(meth.upper())

                if meth != 'head':
                    method = _make_jsonify(method)

                sig = inspect.signature(method)
                if 'request' in sig.parameters:
                    method = partialmethod(method, request=request)
                if 'session' in sig.parameters:
                    method = partialmethod(method, session=session)
                if 'g' in sig.parameters:
                    method = partialmethod(method, g=g)

                setattr(cls, meth, method)

        view.__name__ = name
        view.__module__ = cls.__module__
        view.methods = methods
        view.view_cls = cls

        return view

    def dispatch_request(self, *args, **kwargs):
        method = getattr(self, request.method.lower(), None)

        # if method is HEAD and it is not handled by an app,
        # treat the method by GET
        if method is None and request.method == 'HEAD':
            method = getattr(self, 'get', None)

        return method(*args, **kwargs)
