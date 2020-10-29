# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Rio Matsuoka
# All rights reserved.
"""
flask_api_connector
====================

Simplify to register app views to Flask app API.
"""

import os
import re
from setuptools import setup

with open(os.path.join(
        os.path.dirname(__file__),
        'flask_api_connector',
        '__init__.py'), 'r') as f:
    pattern = r"^__version__\s*=\s*['\"](.*)['\"]$"
    mo = re.search(pattern, f.read(), re.MULTILINE)
    if mo:
        version = mo.group(1)
    else:
        raise RuntimeError('Unable to find version')

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='Flask-ApiConnector',
    version=version,
    url='https://github.com/riomat13/Flask-ApiConnector',
    license='MIT',
    author='Rio Matsuoka',
    description='Easy to register app views to Flask app.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['flask_api_connector'],
    zip_safe=False,
    platform='any',
    install_requires=[
        'Flask',
    ],
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Flask',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6'
)
