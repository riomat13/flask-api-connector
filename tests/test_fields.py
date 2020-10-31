# -*- coding: utf-8 -*-
#
# Original Copyright (c) 2013, Twilio, Inc.
# Modified Copyright (c) 2020, Rio Matsuoka
# All rights reserved.

import unittest
from unittest.mock import Mock, patch

from collections import OrderedDict
from datetime import datetime, timedelta, tzinfo
from decimal import Decimal
from functools import partial

import pytz
from flask import Flask, Blueprint

from flask_api_connector.exceptions import InvalidFieldDataException
from flask_api_connector import fields


class Foo(object):
    def __init__(self):
        self.hey = 3


def check_field(expected, field, value):
    assert expected == field.output('a', {'a': value})


def test_get_value():
    assert fields.get_value("hey", {"hey": 3}) == 3


def test_get_value_no_value():
    assert fields.get_value("foo", {"hey": 3}) is None


def test_get_value_obj():
    assert fields.get_value("hey", Foo()) == 3

def test_get_value_from_nested_object():
    obj = {
        'key1': {
            'key2': {
                'key3': 1
            },
        }
    }
    value = fields.get_value(key='key1', obj=obj)
    assert value == {'key2': {'key3': 1}}

    value = fields.get_value(key='key1.key2', obj=obj)
    assert value == {'key3': 1}

    value = fields.get_value(key='key1.key2.key3', obj=obj)
    assert value == 1


def test_float():
    values = [
        ("-3.13", -3.13),
        (str(-3.13), -3.13),
        (3, 3.0),
    ]
    for value, expected in values:
        check_field(expected, fields.Float(), value)


def test_boolean():
    values = [
        (True, True),
        (False, False),
        ({}, False),
        ("false", True),  # These are different from php
        ("0", True),      # Will this be a problem?
    ]
    for value, expected in values:
        check_field(expected, fields.Boolean(), value)


def test_datetime_formatters():
    dates = [
        (datetime(2011, 1, 1), "2011-01-01T00:00:00"),
        (datetime(2011, 1, 1, 23, 59, 59),
         "2011-01-01T23:59:59"),
        (datetime(2011, 1, 1, 23, 59, 59, 1000),
         "2011-01-01T23:59:59.001000"),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.utc),
         "2011-01-01T23:59:59+00:00"),
        (datetime(2011, 1, 1, 23, 59, 59, 1000, tzinfo=pytz.utc),
         "2011-01-01T23:59:59.001000+00:00"),
        (datetime(2011, 1, 1, 23, 59, 59, tzinfo=pytz.timezone('CET')),
         "2011-01-01T23:59:59+01:00")
    ]

    field = fields.DateTime()
    for date_obj, expected in dates:
        check_field(expected, fields.DateTime(), date_obj)


class FieldsTestCase(unittest.TestCase):

    def test_decimal_trash(self):
        self.assertRaises(InvalidFieldDataException, lambda: fields.Float().output('a', {'a': 'Foo'}))

    def test_basic_dictionary(self):
        obj = {"foo": 3}
        field = fields.String()
        self.assertEqual(field.output("foo", obj), "3")

    def test_date_field_invalid(self):
        obj = {"bar": 3}
        field = fields.DateTime()
        self.assertRaises(InvalidFieldDataException, lambda: field.output("bar", obj))

    def test_basic_field(self):
        obj = Mock()
        obj.foo = 3
        field = fields.Raw()
        self.assertEqual(field.output("foo", obj), 3)

    def test_raw_field(self):
        obj = Mock()
        obj.foo = 3
        field = fields.Raw()
        self.assertEqual(field.output("foo", obj), 3)

    def test_nested_raw_field(self):
        foo = Mock()
        bar = Mock()
        bar.value = 3
        foo.bar = bar
        field = fields.Raw()
        self.assertEqual(field.output("bar.value", foo), 3)

    def test_int(self):
        field = fields.Integer()
        self.assertEqual(3, field.output("hey", {'hey': 3}))

    def test_int_default(self):
        field = fields.Integer(default=1)
        self.assertEqual(1, field.output("hey", {'hey': None}))

    def test_no_int(self):
        field = fields.Integer()
        self.assertEqual(0, field.output("hey", {'hey': None}))

    def test_int_decode_error(self):
        field = fields.Integer()
        self.assertRaises(InvalidFieldDataException, lambda: field.output("hey", {'hey': 'Explode please I am nowhere looking like an int'}))

    def test_float(self):
        field = fields.Float()
        self.assertEqual(3.0, field.output("hey", {'hey': 3.0}))

    def test_float_decode_error(self):
        field = fields.Float()
        self.assertRaises(InvalidFieldDataException, lambda: field.output("hey", {'hey': 'Explode!'}))

    PI_STR = u'3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861'
    PI = Decimal(PI_STR)

    def test_arbitrary(self):
        field = fields.Arbitrary()
        self.assertEqual(self.PI_STR, field.output("hey", {'hey': self.PI}))

    def test_fixed(self):
        field5 = fields.Fixed(5)
        field4 = fields.Fixed(4)

        self.assertEqual('3.14159', field5.output("hey", {'hey': self.PI}))
        self.assertEqual('3.1416', field4.output("hey", {'hey': self.PI}))
        self.assertEqual('3.0000', field4.output("hey", {'hey': '3'}))
        self.assertEqual('3.0000', field4.output("hey", {'hey': '03'}))
        self.assertEqual('3.0000', field4.output("hey", {'hey': '03.0'}))

    def test_zero_fixed(self):
        field = fields.Fixed()
        self.assertEqual('0.00000', field.output('hey', {'hey': 0}))

    def test_infinite_fixed(self):
        field = fields.Fixed()
        self.assertRaises(InvalidFieldDataException, lambda: field.output("hey", {'hey': '+inf'}))
        self.assertRaises(InvalidFieldDataException, lambda: field.output("hey", {'hey': '-inf'}))

    def test_advanced_fixed(self):
        field = fields.Fixed()
        self.assertRaises(InvalidFieldDataException, lambda: field.output("hey", {'hey': 'NaN'}))

    def test_string(self):
        field = fields.String()
        self.assertEqual("3", field.output("hey", Foo()))

    def test_string_no_value(self):
        field = fields.String()
        self.assertEqual(None, field.output("bar", Foo()))

    def test_string_none(self):
        field = fields.String()
        self.assertEqual(None, field.output("empty", {'empty': None}))

    def test_iso8601_date_field_without_offset(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45)}
        field = fields.DateTime()
        self.assertEqual("2011-08-22T20:58:45", field.output("bar", obj))

    def test_iso8601_date_field_with_offset(self):
        obj = {"bar": datetime(2011, 8, 22, 20, 58, 45, tzinfo=pytz.timezone('CET'))}
        field = fields.DateTime()
        self.assertEqual("2011-08-22T20:58:45+01:00", field.output("bar", obj))

    def test_invalid_list(self):
        class Temp:
            # mock raw base like class but not subclassed
            def format(self, *args, **kwargs):
                pass
            def output(self, *args, **kwargs):
                pass

        with self.assertRaises(InvalidFieldDataException):
            fields.List(Temp)

        with self.assertRaises(InvalidFieldDataException):
            fields.List(Temp())

    def test_list(self):
        obj = {'list': ['a', 'b', 'c']}
        field = fields.List(fields.String)
        self.assertEqual(['a', 'b', 'c'], field.output('list', obj))

    def test_list_from_set(self):
        obj = {'list': set(['a', 'b', 'c'])}
        field = fields.List(fields.String)
        self.assertEqual(set(['a', 'b', 'c']), set(field.output('list', obj)))

    def test_list_from_object(self):
        class TestObject(object):
            def __init__(self, list):
                self.list = list
        obj = TestObject(['a', 'b', 'c'])
        field = fields.List(fields.String)
        self.assertEqual(['a', 'b', 'c'], field.output('list', obj))

    def test_null_list(self):
        class TestObject(object):
            def __init__(self, list):
                self.list = list
        obj = TestObject(None)
        field = fields.List(fields.String)
        self.assertEqual(None, field.output('list', obj))

    def test_list_of_nested(self):
        obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
        field = fields.List(fields.Nested({'a': fields.Integer}))
        self.assertEqual([OrderedDict([('a', 1)]),
                          OrderedDict([('a', 2)]),
                          OrderedDict([('a', 3)])],
                         field.output('list', obj))

    def test_apply_list_to_dict_and_parse_nested_items(self):
        obj = {'list': {'a': '1', 'b': 2}}
        field = fields.List(
            fields.Nested({'a': fields.String, 'b': fields.String}))
        self.assertEqual([OrderedDict([('a', '1'), ('b', '2')])],
                         field.output('list', obj))

    def test_nested_with_default(self):
        obj = None
        field = fields.Nested({
            'a': fields.Integer,
            'b': fields.String}, default={'message': 'empty'})
        self.assertEqual({'message': 'empty'}, field.output('a', obj))

    def test_nested_list_with_null(self):
        obj = None
        field = fields.Nested({
            'a': fields.Integer,
            'b': fields.String}, allow_null=True)
        self.assertEqual(None, field.output('a', obj))

    def test_nested_list_with_no_specifying_handle_null(self):
        obj = None
        field = fields.Nested({'a': fields.Integer})
        # should be set a value from inner field default value
        self.assertEqual(OrderedDict([('a', 0)]), field.output('a', obj))

    def test_list_of_raw(self):
        obj = {'list': [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}, {'a': 3, 'b': 1}]}
        field = fields.List(fields.Raw)
        self.assertEqual([OrderedDict([('a', 1), ('b', 1), ]),
                          OrderedDict([('a', 2), ('b', 1), ]),
                          OrderedDict([('a', 3), ('b', 1), ])],
                         field.output('list', obj))

        obj = {'list': [1, 2, 'a']}
        field = fields.List(fields.Raw)
        self.assertEqual([1, 2, 'a'], field.output('list', obj))


if __name__ == '__main__':
    unittest.main()
