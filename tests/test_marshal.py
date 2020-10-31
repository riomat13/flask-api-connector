# -*- coding: utf-8 -*-
#
# Original Copyright (c) 2013, Twilio, Inc.
# Modified Copyright (c) 2020, Rio Matsuoka
# All rights reserved.

from collections import OrderedDict

from flask_api_connector.marshal import marshal
from flask_api_connector.fields import List, Nested, String, Raw


def test_marshal():
        fields = OrderedDict([('foo', Raw)])
        marshal_dict = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
        output = marshal(marshal_dict, fields)
        assert output == {'foo': 'bar'}


def test_marshal_with_list_data_in_dict():
        fields = OrderedDict([('foo', List(String))])
        marshal_dict = OrderedDict([('foo', ['bar', 'baz']), ('bat', 'baz')])
        output = marshal(marshal_dict, fields)
        assert output == {'foo': ['bar', 'baz']}


def test_marshal_with_key():
    fields = OrderedDict([('foo', Raw)])
    marshal_dict = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = marshal(marshal_dict, fields, key='hey')
    assert output == {'hey': {'foo': 'bar'}}


def test_marshal_with_list_data_in_dict_with_envelop():
        fields = OrderedDict([('foo', List(String))])
        marshal_dict = OrderedDict([('foo', ['bar', 'baz']), ('bat', 'baz')])
        output = marshal(marshal_dict, fields, key='hey')
        assert output == {'hey': {'foo': ['bar', 'baz']}}


def test_marshal_field():
        fields = OrderedDict({'foo': Raw()})
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
        output = marshal(marshal_fields, fields)
        assert output == {'foo': 'bar'}


def test_marshal_tuple():
    fields = OrderedDict({'foo': Raw})
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = marshal((marshal_fields,), fields)
    assert output == [{'foo': 'bar'}]


def test_marshal_tuple_with_key():
    fields = OrderedDict({'foo': Raw})
    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz')])
    output = marshal((marshal_fields,), fields, key='hey')
    assert output == {'hey': [{'foo': 'bar'}]}


def test_marshal_nested():
    fields = OrderedDict([
        ('foo', Raw),
        ('fee', Nested({
            'fye': String,
        }))
    ])

    marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'fye': 'fum'})])
    output = marshal(marshal_fields, fields)
    expected = OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', 'fum')]))])
    assert output == expected


    def test_marshal_nested_with_non_null():
        fields = OrderedDict([
            ('foo', Raw),
            ('fee', Nested(
                OrderedDict([
                    ('fye', String),
                    ('blah', String)
                ]), allow_null=False))
        ])
        marshal_fields = [OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', None)])]
        output = marshal(marshal_fields, fields)
        expected = [OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', None)]))])]
        assert output == expected

    def test_marshal_nested_with_null():
        fields = OrderedDict([
            ('foo', Raw),
            ('fee', Nested(
                OrderedDict([
                    ('fye', String),
                    ('blah', String)
                ]), allow_null=True))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', None)])
        output = marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', None)])
        assert output == expected

    def test_allow_null_presents_data():
        fields = OrderedDict([
            ('foo', Raw),
            ('fee', Nested(
                OrderedDict([
                    ('fye', String),
                    ('blah', String)
                ]), allow_null=True))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'blah': 'cool'})])
        output = marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', 'cool')]))])
        assert output == expected

    def test_marshal_nested_property():
        class TestObject(object):
            @property
            def fee(self):
                return {'blah': 'cool'}

        fields = OrderedDict([
            ('foo', Raw),
            ('fee', Nested(
                OrderedDict([
                    ('fye', String),
                    ('blah', String)
                ]), allow_null=True))
        ])
        obj = TestObject()
        obj.foo = 'bar'
        obj.bat = 'baz'
        output = marshal([obj], fields)
        expected = [OrderedDict([('foo', 'bar'), ('fee', OrderedDict([('fye', None), ('blah', 'cool')]))])]
        assert output == expected

    def test_marshal_list():
        fields = OrderedDict([
            ('foo', Raw),
            ('fee', List(String))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', ['fye', 'fum'])])
        output = marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', (['fye', 'fum']))])
        assert output == expected

    def test_marshal_list_of_nesteds():
        fields = OrderedDict([
            ('foo', Raw),
            ('fee', List(Nested({'fye': String})))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', {'fye': 'fum'})])
        output = marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', [OrderedDict([('fye', 'fum')])])])
        assert output == expected

    def test_marshal_list_of_lists():
        fields = OrderedDict([
            ('foo', Raw),
            ('fee', List(List(String)))
        ])
        marshal_fields = OrderedDict([('foo', 'bar'), ('bat', 'baz'), ('fee', [['fye'], ['fum']])])
        output = marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'bar'), ('fee', [['fye'], ['fum']])])
        assert output == expected

    def test_marshal_nested_dict():
        fields = OrderedDict([
            ('foo', Raw),
            ('bar', OrderedDict([('a', Raw), ('b', Raw)])),
        ])
        marshal_fields = OrderedDict([('foo', 'foo-val'), ('bar', 'bar-val'), ('bat', 'bat-val'),
                                      ('a', 1), ('b', 2), ('c', 3)])
        output = flask_restful.marshal(marshal_fields, fields)
        expected = OrderedDict([('foo', 'foo-val'), ('bar', OrderedDict([('a', 1), ('b', 2)]))])
        assert output == expected
