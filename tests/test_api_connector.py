# -*- coding: utf-8 -*-

from unittest.mock import MagicMock

from flask_api_connector.core import ApiConnector


def test_set_paths_to_app(app, paths):
    app.add_url_rule = MagicMock()

    mock_funcs = []
    # mock all as_view method in view class
    for path in paths:
        mock_fn = MagicMock()
        path.view_cls.as_view = mock_fn
        mock_funcs.append(mock_fn)

    ApiConnector(paths).init_app(app)

    assert app.add_url_rule.call_count == len(paths)

    for path, mock_fn in zip(paths, mock_funcs):

        app.add_url_rule.assert_any_call(
            f'/api{path.rule}',
            view_func=mock_fn.return_value
        )

        mock_fn.assert_called_once_with(path.name)


def test_set_root_url(app, paths):
    app.add_url_rule = MagicMock()

    # mock all as_view method in view class
    for path in paths:
        path.view_cls.as_view = MagicMock()

    # test with user defined base url
    ApiConnector(paths, root_url='/test').init_app(app)
    assert len(app.add_url_rule.call_args_list) == len(paths)

    for path, call_args in zip(paths, app.add_url_rule.call_args_list):
        assert call_args[0][0] == f'/test{path.rule}'
