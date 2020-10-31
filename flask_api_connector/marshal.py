# -*- coding: utf-8 -*-
#
# Original Copyright (c) 2013, Twilio, Inc.
# Modified Copyright (c) 2020, Rio Matsuoka
# All rights reserved.

from collections import OrderedDict


def make(cls):
    if isinstance(cls, type):
        return cls()
    return cls


def marshal(data, fields, key=None) -> OrderedDict:
    """Convert raw data into specified format.

    Args:
        data: object
            input raw data
        fields: dict
            key-value pair of data
            The keys will be used as output.
            The values will be the output field type and
            convert the raw data accordingly.
        key: object (default: None)
            if provided, key will be used at the top of the output data

    Example:
        >>> from flask_api_connector import fields, marshal
        >>>
        >>> data = { 'a': 100, 'b': 'foo' }
        >>> mfields = { 'a': fields.Raw }
        >>>
        >>> marshal(data, mfields)
        OrderedDict([('a', 100)])
        >>>
        >>> marshal(data, mfields, key='data')
        OrderedDict([('data', OrderedDict([('a', 100)]))])
    """

    if isinstance(data, (list, tuple)):
        return (OrderedDict([(key, [marshal(d, fields) for d in data])])
                if key else [marshal(d, fields) for d in data])

    items = ((k, marshal(data, v) if isinstance(v, dict)
              else make(v).output(k, data))
             for k, v in fields.items())
    return OrderedDict([(key, OrderedDict(items))]) \
        if key else OrderedDict(items)
