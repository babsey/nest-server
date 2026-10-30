import unittest
from unittest.mock import MagicMock

from nest_server.helpers import get_arguments


class FakeMultiDict(dict):
    """Minimal stand-in for werkzeug's MultiDict (form / args)."""

    def __init__(self, data=None):
        super().__init__()
        self._lists = {}
        for key, values in (data or {}).items():
            if not isinstance(values, (list, tuple)):
                values = [values]
            self._lists[key] = list(values)
            self[key] = self._lists[key][0]

    def getlist(self, key):
        return list(self._lists.get(key, []))

    def to_dict(self):
        return dict(self)


def make_request(json=None, is_json=False, form=None, args=None):
    """Build a mock request object."""
    request = MagicMock()
    request.is_json = is_json
    request.get_json.return_value = json
    request.form = FakeMultiDict(form)
    request.args = FakeMultiDict(args)
    return request


class TestGetArgumentsJson(unittest.TestCase):
    def test_json_non_empty_string(self):
        request = make_request(json="hello", is_json=True)
        self.assertEqual(get_arguments(request), (["hello"], {}))

    def test_json_empty_string(self):
        request = make_request(json="", is_json=True)
        self.assertEqual(get_arguments(request), ([], {}))

    def test_json_list(self):
        request = make_request(json=[1, 2, 3], is_json=True)
        self.assertEqual(get_arguments(request), ([1, 2, 3], {}))

    def test_json_empty_list(self):
        request = make_request(json=[], is_json=True)
        self.assertEqual(get_arguments(request), ([], {}))

    def test_json_dict_kwargs_only(self):
        request = make_request(json={"a": 1, "b": "two"}, is_json=True)
        self.assertEqual(get_arguments(request), ([], {"a": 1, "b": "two"}))

    def test_json_empty_dict(self):
        request = make_request(json={}, is_json=True)
        self.assertEqual(get_arguments(request), ([], {}))

    def test_json_dict_with_args_key(self):
        request = make_request(json={"args": [1, 2], "x": 10}, is_json=True)
        self.assertEqual(get_arguments(request), ([1, 2], {"x": 10}))

    def test_json_dict_with_only_args_key(self):
        request = make_request(json={"args": ["a", "b"]}, is_json=True)
        self.assertEqual(get_arguments(request), (["a", "b"], {}))

    def test_json_dict_args_is_removed_from_kwargs(self):
        request = make_request(json={"args": [1], "k": "v"}, is_json=True)
        _, kwargs = get_arguments(request)
        self.assertNotIn("args", kwargs)

    def test_json_unsupported_types_return_empty(self):
        for value in (42, 3.14, True, None):
            with self.subTest(value=value):
                request = make_request(json=value, is_json=True)
                self.assertEqual(get_arguments(request), ([], {}))

    def test_json_takes_precedence_over_form_and_args(self):
        request = make_request(
            json={"from": "json"},
            is_json=True,
            form={"from": "form"},
            args={"from": "query"},
        )
        self.assertEqual(get_arguments(request), ([], {"from": "json"}))

    def test_json_empty_does_not_fall_through_to_form(self):
        request = make_request(json=[], is_json=True, form={"a": "1"})
        self.assertEqual(get_arguments(request), ([], {}))


class TestGetArgumentsForm(unittest.TestCase):
    def test_form_kwargs(self):
        request = make_request(form={"a": "1", "b": "2"})
        self.assertEqual(get_arguments(request), ([], {"a": "1", "b": "2"}))

    def test_form_args_key(self):
        request = make_request(form={"args": ["x", "y", "z"]})
        self.assertEqual(get_arguments(request), (["x", "y", "z"], {}))

    def test_form_args_key_ignores_other_fields(self):
        request = make_request(form={"args": ["x"], "other": "ignored"})
        self.assertEqual(get_arguments(request), (["x"], {}))

    def test_form_takes_precedence_over_query_args(self):
        request = make_request(form={"a": "form"}, args={"a": "query"})
        self.assertEqual(get_arguments(request), ([], {"a": "form"}))


class TestGetArgumentsQueryString(unittest.TestCase):
    def test_query_kwargs(self):
        request = make_request(args={"a": "1", "b": "2"})
        self.assertEqual(get_arguments(request), ([], {"a": "1", "b": "2"}))

    def test_query_args_key(self):
        request = make_request(args={"args": ["p", "q"]})
        self.assertEqual(get_arguments(request), (["p", "q"], {}))

    def test_query_args_key_ignores_other_params(self):
        request = make_request(args={"args": ["p"], "other": "ignored"})
        self.assertEqual(get_arguments(request), (["p"], {}))


class TestGetArgumentsEmpty(unittest.TestCase):
    def test_no_data_returns_empty(self):
        request = make_request()
        self.assertEqual(get_arguments(request), ([], {}))

    def test_return_types(self):
        request = make_request(json=(1, 2), is_json=True)  # tuple is unsupported
        args, kwargs = get_arguments(request)
        self.assertIsInstance(args, list)
        self.assertIsInstance(kwargs, dict)


if __name__ == "__main__":
    unittest.main()
