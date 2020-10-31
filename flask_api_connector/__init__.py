# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Rio Matsuoka
# All rights reserved.
"""
flask_api_connector
===================

Simplify to register app views to Flask app API.
"""

from .core import ApiConnector, Paths
from .marshal import marshal

__all__ = ['ApiConnector', 'Paths', 'marshal']

__version__ = '0.0.1dev0a'
