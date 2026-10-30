import pytest

from nest_server.mpi.helpers import combine


@pytest.mark.parametrize("data", [None, [], [None], [None, None, None]])
def test_combine_returns_none(data):
    assert combine(data) is None


@pytest.mark.parametrize(
    "data, expected",
    [
        ([1], 1),
        (["a"], "a"),
        ([{"a": 1}], {"a": 1}),
        ([[1, 2]], [1, 2]),
    ],
)
def test_combine_single_item(data, expected):
    assert combine(data) == expected


def test_combine_filters_none_values():
    assert combine([None, {"a": 1}, None]) == {"a": 1}
    assert combine([None, 5]) == 5


@pytest.mark.parametrize(
    "data",
    [
        [1, 1],
        [{"a": 1}, {"a": 1}, {"a": 1}],
        [[1, 2], [1, 2]],
        ["x", "x"],
    ],
)
def test_combine_identical_items_returns_first(data):
    assert combine(data) == data[0]


def test_combine_lists_are_interleaved():
    assert combine([[1, 3], [2, 4]]) == [1, 2, 3, 4]
    assert combine([[1, 4], [2, 5], [3, 6]]) == [1, 2, 3, 4, 5, 6]


def test_combine_tuples_are_interleaved():
    assert combine([(1, 3), (2, 4)]) == [1, 2, 3, 4]


def test_combine_lists_drop_inner_none():
    assert combine([[1, None], [None, 4]]) == [1, 4]


def test_combine_lists_of_unequal_length_raise():
    with pytest.raises(ValueError):
        combine([[1, 2], [3]])


def test_combine_dicts_are_merged():
    assert combine([{"a": 1}, {"b": 2}]) == {"a": 1, "b": 2}
    assert combine([{"a": 1}, {"a": 1, "b": 2}]) == {"a": 1, "b": 2}


def test_combine_dicts_ignore_empty():
    assert combine([{}, {"a": 1}]) == {"a": 1}


def test_combine_mixed_types_returned_as_list():
    assert combine([1, "a"]) == [1, "a"]
    assert combine([1, [2]]) == [1, [2]]
    assert combine([{"a": 1}, 2]) == [{"a": 1}, 2]


def test_combine_different_scalars_returned_as_list():
    assert combine([1, 2, 3]) == [1, 2, 3]
