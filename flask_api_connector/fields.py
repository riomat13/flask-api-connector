# -*- coding: utf-8 -*-
#
# Original Copyright (c) 2013, Twilio, Inc.
# Modified Copyright (c) 2020, Rio Matsuoka
# All rights reserved.

# flake8: noqa

from calendar import timegm
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN

from urllib.parse import urlparse, urlunparse
from flask import url_for, request

from .exceptions import InvalidFieldDataException
from .marshal import marshal

__all__ = ("Raw", "String", "DateTime", "Float", "Integer",
           "Arbitrary", "Nested", "List", "Boolean", "Fixed")


def get_value(key, obj, default=None):
    """Helper for pulling a keyed value off various types of objects"""
    if isinstance(key, int):
        return _get_value_for_key(key, obj, default)
    else:
        return _get_value_for_keys(key.split('.'), obj, default)


def _get_value_for_keys(keys, obj, default):
    if len(keys) == 1:
        return _get_value_for_key(keys[0], obj, default)
    else:
        return _get_value_for_keys(
            keys[1:], _get_value_for_key(keys[0], obj, default), default)


def _get_value_for_key(key, obj, default):
    try:
        return obj[key]
    except (IndexError, TypeError, KeyError):
        return getattr(obj, key, default)


class Raw(object):
    """Base field type.

    Args:
        default: any (default: None)
            default value to set if specified
            this will set the value when no value is passed from data
    """

    def __init__(self, default=None):
        self.default = default

    def format(self, value):
        """Formatting the given data.
        No operation will be applied by default in base field."""
        return value

    def output(self, key, obj):
        """Pulls the value for the given key from the object, applies the
        field's formatting and returns the result. If the key is not found
        in the object, returns the default value. Field classes that create
        values which do not require the existence of the key in the object
        should override this and return the desired value.

        Raises:
            InvalidFieldDataException: In case of formatting problem
        """

        value = get_value(key, obj)

        if value is None:
            return self.default

        return self.format(value)


class Nested(Raw):
    """Allows you to nest one set of fields inside another.

    Args:
        nested: dict
            nest item key and field as value
        allow_null: bool (default: False)
            allow to return None if set to True
            otherwise return the default value
        default: (optional)
            if this value is specified, this value will be used as default
            when the output is None
    """

    def __init__(self, nested, allow_null=False, **kwargs):
        self.nested = nested
        self.allow_null = allow_null
        super(Nested, self).__init__(**kwargs)

    def output(self, key, obj):
        value = get_value(key, obj)

        if value is None:
            if self.allow_null:
                return None
            elif self.default is not None:
                return self.default

        return marshal(value, self.nested)


class List(Raw):
    """Field for marshalling lists of other fields.

    Args:
        field: subclass of Raw class or instance
            The field type the list will contain.
    """

    def __init__(self, field, **kwargs):
        super(List, self).__init__(**kwargs)
        error_msg = ("The type of the list elements must be a subclass of "
                     "flask_api_connector.fields.Raw")
        if isinstance(field, type):
            if not issubclass(field, Raw):
                raise InvalidFieldDataException(error_msg)
            self.container = field()
        else:
            if not isinstance(field, Raw):
                raise InvalidFieldDataException(error_msg)
            self.container = field

    def format(self, value):
        # Convert all instances in typed list to container type
        if isinstance(value, set):
            value = list(value)

        return [
            self.container.output(idx,
                val if isinstance(val, dict)
                        and not isinstance(self.container, Nested)
                        and not type(self.container) is Raw
                    else value)
            for idx, val in enumerate(value)
        ]

    def output(self, key, data):
        value = get_value(key, data)
        if value is None:
            return self.default

        # we cannot really test for external dict behavior
        if hasattr(value, '__iter__') and not isinstance(value, (str, dict)):
            return self.format(value)

        return [marshal(value, self.container.nested)]


class String(Raw):
    """Marshal a value as a string."""
    def format(self, value):
        # won't handle TypeError here
        return str(value)


class Integer(Raw):
    """Integer value field."""
    def __init__(self, default=0, **kwargs):
        super(Integer, self).__init__(default=default, **kwargs)

    def format(self, value):
        try:
            return int(value)
        except ValueError as e:
            raise InvalidFieldDataException(e)


class Boolean(Raw):
    """Boolean value field."""
    def format(self, value):
        return bool(value)


class Float(Raw):
    """
    A double as IEEE-754 double precision.
    ex : 3.141592653589793 3.1415926535897933e-06 3.141592653589793e+24 nan inf
    -inf
    """

    def format(self, value):
        try:
            return float(value)
        except ValueError as ve:
            raise InvalidFieldDataException(ve)


class Arbitrary(Raw):
    """
        A floating point number with an arbitrary precision
          ex: 634271127864378216478362784632784678324.23432
    """

    def format(self, value):
        return str(Decimal(value))


class DateTime(Raw):
    """Return datetime in UTC with formatted by datetime.isoformat()."""
    def __init__(self, **kwargs):
        super(DateTime, self).__init__(**kwargs)

    def format(self, value: datetime):
        try:
            return value.isoformat()
        except AttributeError as e:
            raise InvalidFieldDataException(e)


ZERO = Decimal()


class Fixed(Raw):
    """A decimal number with a fixed precision."""
    def __init__(self, decimals=5, **kwargs):
        super(Fixed, self).__init__(**kwargs)
        self.precision = Decimal('0.' + '0' * (decimals - 1) + '1')

    def format(self, value):
        dvalue = Decimal(value)
        if not dvalue.is_normal() and dvalue != ZERO:
            raise InvalidFieldDataException('Invalid Fixed precision number.')
        return str(dvalue.quantize(self.precision, rounding=ROUND_HALF_EVEN))
