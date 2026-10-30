import pytest

from nest_server.helpers import str2bool


@pytest.mark.parametrize("value", ["1", "t", "true", "y", "yes", "TRUE", "True", "Yes", "Y", "T"])
def test_str2bool_is_case_insensitive(value):
    assert str2bool(value)


@pytest.mark.parametrize("value", ["", "0", "f", "false", "n", "no", "off", "2", " true", "yes please"])
def test_str2bool_false_values(value):
    assert not str2bool(value)


def test_str2bool_none():
    assert str2bool(None) is False
