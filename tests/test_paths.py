# -*- coding: utf-8 -*-

from unittest.mock import patch

from flask_api_connector.core import Paths


def test_execute_process_for_all_paths():
    with patch('flask_api_connector.core.Paths.process') as mock_process:
        # entity function to check input
        mock_process.side_effect = lambda x: x

        paths = Paths(list(range(10)))

        for i, path in enumerate(paths):
            assert i == path
            assert mock_process.called
            mock_process.reset_mock()


def test_process_path_items():
    class Test1(object):
        def get(self, request):
            pass

    class Test2(object):
        def post(self, request):
            pass

    class Test3(object):
        def get(self):
            pass

        def post(self, request):
            pass

    paths = Paths([
        ('/', Test1),
        ('/test2', Test2),
        ('/test3/sub', Test3)
    ])

    paths = list(paths)
    assert len(paths) == 3

    assert paths[0].rule == '/'
    assert paths[0].name == 'test1'
    assert hasattr(paths[0].view_cls, 'get')
    assert not hasattr(paths[0].view_cls, 'post')

    assert paths[1].rule == '/test2'
    assert paths[1].name == 'test2'
    assert not hasattr(paths[1].view_cls, 'get')
    assert hasattr(paths[1].view_cls, 'post')

    assert paths[2].rule == '/test3/sub'
    assert paths[2].name == 'test3'
    assert hasattr(paths[2].view_cls, 'get')
    assert hasattr(paths[2].view_cls, 'post')
